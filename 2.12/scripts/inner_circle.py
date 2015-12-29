##Analysis=group
##input_layer=vector
##raster_steps=number 20
##precision=number 0.1
##inner_circle_centers=output vector
from qgis.core import *
from processing.tools.vector import VectorWriter
from PyQt4.QtCore import QVariant


def computeCentralPoint(bbox,polygon,border,max_dist):
    best_dist = max_dist 
    best_pt = None
    for i in range (0,steps):
        for j in range(0,steps):
            x = bbox.xMinimum() + bbox.width() * i/steps
            y = bbox.yMinimum() + bbox.height() * j/steps
            pt = QgsGeometry.fromPoint(QgsPoint(x,y))
            if polygon.intersects(pt):
                dist = pt.distance(border)
                if dist > best_dist:
                    #print "%s: %f" %(pt.asPoint(),dist)
                    best_dist = dist
                    best_pt = pt
    return (best_pt,best_dist)
    
def makeSearchRectange(best_point,bbox):
    bbox = QgsRectangle(
            best_point.asPoint().x() - bbox.width()/steps,
            best_point.asPoint().y() - bbox.height()/steps,
            best_point.asPoint().x() + bbox.width()/steps,
            best_point.asPoint().y() + bbox.height()/steps)
    return bbox

# get the input layer and its fields
my_layer = processing.getObject(input_layer)
n = my_layer.featureCount()
fields = my_layer.dataProvider().fields()
fields.append(QgsField("radius", QVariant.Double))
# create the output vector writer with the same fields
writer = VectorWriter(inner_circle_centers, None, fields, QGis.WKBPoint, my_layer.crs())
# create output features
feat = QgsFeature()

i=0

print 'Getting started ...'

for input_feature in my_layer.getFeatures():
    progress.setPercentage(int(100*i/n))
    i+=1
    steps = raster_steps
    polygon = input_feature.geometry()
    border = QgsGeometry.fromPolyline(polygon.asPolygon()[0])
    bbox = input_feature.geometry().boundingBox()
    
    # first round
    best_point, max_dist = computeCentralPoint(bbox,polygon,border,0)
    if best_point == None:
        continue
    # second round
    prev_point = best_point
    bbox = makeSearchRectange(best_point,bbox)
    best_point, max_dist = computeCentralPoint(bbox,polygon,border,max_dist-0.001)
    if best_point == None:
        continue
    d = best_point.distance(prev_point)
    # repeat until position doesn't change anymore
    while d > precision:
        prev_point = best_point
        bbox = makeSearchRectange(best_point,bbox)
        pt, max_dist = computeCentralPoint(bbox,polygon,border,max_dist)
        if pt:
            best_point = pt
        else:
            break 
    
    #print "Best point (%f,%f): %f" %(best_point.asPoint().x(),best_point.asPoint().y(),max_dist)        
    
    
    # copy attributes from the input point feature
    attributes = input_feature.attributes()
    attributes.append(max_dist)
    feat.setAttributes(attributes)
    feat.setGeometry(best_point)
    writer.addFeature(feat)
    
    
    
    
    
del writer
