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
writer = VectorWriter(output, None, [QgsField("line_id", QVariant.Int)], network_layer.dataProvider().geometryType(), network_layer.crs() )

# prepare graph
vl = network_layer
director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
properter = QgsDistanceArcProperter()
director.addProperter( properter )
crs = vl.crs()
builder = QgsGraphBuilder( crs )

# prepare points
features = processing.features(line_layer)
line_count = line_layer.featureCount()

points = []
linepoints = {}

point_no = 0

for f in features:
    line_attributes = f.attributes()
    line_id = int(line_attributes[line_id_field_index])
    linepoints[line_id]=[]
    for pt in f.geometry().asPolyline():
        points.append(pt)
        linepoints[line_id].append(point_no)
        point_no += 1

tiedPoints = director.makeGraph( builder, points )
graph = builder.graph()

for line_id, point_ids in linepoints.iteritems():
    for i in point_ids[0:-1]:
        tStart = tiedPoints[ i ]
        tStop = tiedPoints[ i+1 ]

        idStart = graph.findVertex( tStart )
        tree = QgsGraphAnalyzer.shortestTree( graph, idStart, 0 )

        idStart = tree.findVertex( tStart )
        idStop = tree.findVertex( tStop )

        if idStop == -1 or idStart == -1:
          continue # ignore this point pair
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
          fet.setAttributes([line_id])
          writer.addFeature(fet)

del writer