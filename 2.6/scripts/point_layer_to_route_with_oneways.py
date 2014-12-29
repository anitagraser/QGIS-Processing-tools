#Definition of inputs and outputs
#==================================
##Routing tools=group
##points=vector
##network=vector
##direction_field=field network 
##value_for_forward_direction=string forward
##value_for_reverse_direction=string reverse
##value_for_two_way_direction=string two_way
##route_with_oneways=output vector

#Algorithm body
#==================================
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *
from qgis.networkanalysis import *

from processing.tools.vector import VectorWriter

point_layer = processing.getObject(points)
network_layer = processing.getObject(network)
writer = VectorWriter(route_with_oneways, None, [QgsField("order", QVariant.Int)], network_layer.dataProvider().geometryType(), network_layer.crs() )

# prepare graph
vl = network_layer
direction_field = vl.fieldNameIndex(direction_field)
director = QgsLineVectorLayerDirector( vl, direction_field, value_for_forward_direction, value_for_reverse_direction, value_for_two_way_direction, 3 )
properter = QgsDistanceArcProperter()
director.addProperter( properter )
crs = vl.crs()
builder = QgsGraphBuilder( crs )

# prepare points
features = processing.features(point_layer)
point_count = point_layer.featureCount()

points = []

for f in features:
  points.append(f.geometry().asPoint())

tiedPoints = director.makeGraph( builder, points )
graph = builder.graph()

route_vertices = []

for i in range(0,point_count-1):
    progress.setPercentage(int(100 * i/ point_count))
    
    from_point = tiedPoints[i]
    to_point = tiedPoints[i+1]

    from_id = graph.findVertex(from_point)
    to_id = graph.findVertex(to_point)

    (tree,cost) = QgsGraphAnalyzer.dijkstra(graph,from_id,0)

    if tree[to_id] == -1:
        continue # ignore this point pair
    else:
        # collect all the vertices between the points
        route_points = []
        curPos = to_id 
        while (curPos != from_id):
            route_points.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
            curPos = graph.arc( tree[ curPos ] ).outVertex()

        route_points.append(from_point)

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPolyline(route_points))
    fet.setAttributes([i])
    writer.addFeature(fet)

del writer

