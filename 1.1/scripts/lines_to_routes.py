#Definition of inputs and outputs
#==================================
##[my scripts]=group
##lines=vector
##line_id_field=field lines
##network=vector
##output=output vector

#Algorithm body
#==================================
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *
from qgis.networkanalysis import *

from processing.core.VectorWriter import VectorWriter

line_layer = processing.getObject(lines)
line_id_field_index = line_layer.fieldNameIndex(line_id_field)
network_layer = processing.getObject(network)
writer = VectorWriter(output, None, [QgsField("line_id", QVariant.Int),QgsField("length",QVariant.Double)], network_layer.dataProvider().geometryType(), network_layer.crs() )

# prepare graph
vl = network_layer
director = QgsLineVectorLayerDirector(vl,-1,'','','',3)
properter = QgsDistanceArcProperter()
director.addProperter(properter)
crs = vl.crs()
builder = QgsGraphBuilder(crs)

# prepare points
features = processing.features(line_layer)
line_count = line_layer.featureCount()

points = []
linepoints = {}

point_no = 0

for f in features:
    line_id = int(f.attributes()[line_id_field_index])
    linepoints[line_id]=[]
    for pt in f.geometry().asPolyline():
        points.append(pt)
        linepoints[line_id].append(point_no)
        point_no += 1

tiedPoints = director.makeGraph(builder, points)
graph = builder.graph()
nElement = 0
nFeat = line_count 

for line_id, point_ids in linepoints.iteritems():
    progress.setPercentage(int(100 * nElement / nFeat))
    route_points = []
    nElement += 1
    
    for i in point_ids[0:-1]:
        from_point = tiedPoints[i]
        to_point = tiedPoints[i+1]

        from_id = graph.findVertex(from_point)
        to_id = graph.findVertex(to_point)

        (tree,cost) = QgsGraphAnalyzer.dijkstra(graph,from_id,0)

        if tree[to_id] == -1:
            continue # ignore this point pair
        else:
            # collect all the vertices between the points
            pts = []
            curPos = to_id 
            while (curPos != from_id):
                pts.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
                curPos = graph.arc( tree[ curPos ] ).outVertex()

            pts.append(from_point)
            pts.reverse() # because points were collected in reverse order
            route_points+=pts
                        
    # write the output feature
    feat = QgsFeature()
    geom = QgsGeometry.fromPolyline(route_points)
    feat.setGeometry(geom)
    feat.setAttributes([line_id,geom.length()])
    writer.addFeature(feat)
    del feat 
    del tree
        
del graph 
del writer

