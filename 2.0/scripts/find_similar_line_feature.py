#Definition of inputs and outputs
#==================================
##[my scripts]=group
##origin_layer=vector
##target_layer=vector
##target_id_column_index=field target_layer
##interval=number 1.0
##hausdorff_distance_weight=number 1.0
##length_difference_weight=number 1.0
##output=output vector

#Algorithm body
#==================================
from qgis.core import *
from PyQt4.QtCore import *
from processing.core.VectorWriter import VectorWriter
import processing 
from scipy.spatial.distance import cdist
import numpy as np
from math import sqrt

def densify(polyline, interval):
    # densify the polyline using the given interval
    output = []
    for i in xrange(len(polyline) - 1):
        p1 = polyline[i]
        p2 = polyline[i + 1]
        output.append(p1)
        # calculate necessary number of points between p1 and p2
        pointsNumber = sqrt(p1.sqrDist(p2)) / interval
        if pointsNumber > 1:
            multiplier = 1.0 / float(pointsNumber)
        else:
            multiplier = 1
        for j in xrange(int(pointsNumber)):
            delta = multiplier * (j + 1)
            x = p1.x() + delta * (p2.x() - p1.x())
            y = p1.y() + delta * (p2.y() - p1.y())
            output.append(QgsPoint(x, y))
            if j + 1 == pointsNumber:
                break
    output.append(polyline[len(polyline) - 1])
    return output

def calculateHausdorffDistance(geom1,geom2):
    # calculate Hausdorff distance between two polylines
    distances=[]
    # calculate distances between origin and target feature
    D = cdist(geom1,geom2,'euclidean')
    H1 = np.max(np.min(D, axis=1))
    H2 = np.max(np.min(D, axis=0))
    distances.append( max(H1,H2) )
    # repeat the calculation in reverse order
    D = cdist(geom2,geom1,'euclidean')
    H1 = np.max(np.min(D, axis=1))
    H2 = np.max(np.min(D, axis=0))
    distances.append( max(H1,H2) )

    hausdorff = max(distances)
    return hausdorff


origin_layer = processing.getObject(origin_layer)
target_layer = processing.getObject(target_layer)
target_id_column_index = target_layer.fieldNameIndex(target_id_column_index)
"""
origin_layer = l1
target_layer = l2
target_id_column_index = 0
interval = 1
"""

target_spatial_index = QgsSpatialIndex()
target_features = processing.features(target_layer)

origin_fields = origin_layer.pendingFields().toList()
origin_fields.append( QgsField("BEST_FIT", QVariant.Int ))
origin_fields.append( QgsField("HAUSDORFF", QVariant.Double ))
origin_fields.append( QgsField("LEN_DIFF", QVariant.Double ))
writer = VectorWriter(output, None, origin_fields, origin_layer.dataProvider().geometryType(), origin_layer.crs() )

outFeat = QgsFeature()

# populate the spatial index
for feat in target_features: 
    target_spatial_index.insertFeature(feat)
    
origin_features = processing.features(origin_layer)
for origin_feature in origin_features:
    center = origin_feature.geometry().centroid().asPoint()
    print str(center)
    nearest_ids = target_spatial_index.nearestNeighbor(center,10)
    
    best_fit_id = None
    min_weight = None
    
    origin_geom = densify(origin_feature.geometry().asPolyline(), interval)
    
    for id in nearest_ids:
        target_feature = target_layer.getFeatures(QgsFeatureRequest().setFilterFid(id)).next()
        print "Target id: "+str(target_feature.attributes()[target_id_column_index])
        target_geom = densify(target_feature.geometry().asPolyline(), interval)

        hausdorff = calculateHausdorffDistance(origin_geom,target_geom)
        #print "Hausdorff distance: "+str(hausdorff)

        length_difference = abs(origin_feature.geometry().length() - target_feature.geometry().length())

        weight = hausdorff * hausdorff_distance_weight + length_difference * length_difference_weight

        if min_weight == None or weight < min_weight:
            min_weight = weight
            best_hausdorff_distance = hausdorff
            best_fit_id = target_feature.attributes()[target_id_column_index]
            best_length_difference = length_difference
    
    print "Best fit: "+str(best_fit_id)
    print "- distance: "+str(best_hausdorff_distance)
    print "- len diff: "+str(best_length_difference)
    
    outFeat.setGeometry( origin_feature.geometry() )
    atMap = origin_feature.attributes()
    atMap.append(int(best_fit_id))
    atMap.append(float(best_hausdorff_distance))
    atMap.append(float(best_length_difference))
    outFeat.setAttributes( atMap )
    writer.addFeature( outFeat )

del writer
