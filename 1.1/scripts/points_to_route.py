#Definition of inputs and outputs
#==================================
##[my scripts]=group
##points=vector
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


point_layer = processing.getobject(points)
network_layer = processing.getobject(network)
writer = VectorWriter(output, None, [QgsField("order", QVariant.Int)], network_layer.dataProvider().geometryType(), network_layer.crs() )

# prepare graph
vl = network_layer
director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
properter = QgsDistanceArcProperter()
director.addProperter( properter )
crs = vl.crs()
builder = QgsGraphBuilder( crs )

# prepare points
features = processing.getfeatures(point_layer)
point_count = point_layer.featureCount()

points = []

for f in features:
  points.append(f.geometry().asPoint())

tiedPoints = director.makeGraph( builder, points )
graph = builder.graph()

route_vertices = []

for i in range(0,point_count-1):
	tStart = tiedPoints[ i ]
	tStop = tiedPoints[ i+1 ]

	idStart = graph.findVertex( tStart )
	tree = QgsGraphAnalyzer.shortestTree( graph, idStart, 0 )

	idStart = tree.findVertex( tStart )
	idStop = tree.findVertex( tStop )

	if idStop == -1:
	  break
	else:
	  p = []
	  while ( idStart != idStop ):
	    l = tree.vertex( idStop ).inArc()
	    if len( l ) == 0:
	      break
	    e = tree.arc( l[ 0 ] )
	    p.insert( 0, tree.vertex( e.inVertex() ).point() )
	    idStop = e.outVertex()

	  p.insert( 0, tStart )

	  # add a feature
	  fet = QgsFeature()
	  fet.setGeometry(QgsGeometry.fromPolyline(p))
	  fet.setAttributes([i])
	  writer.addFeature(fet)

del writer