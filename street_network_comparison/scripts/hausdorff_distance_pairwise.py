#Definition of inputs and outputs
#==================================
##[my scripts]=group
##input1=vector
##join_field1=field input1
##input2=vector
##join_field2=field input2
##output=output vector

#Algorithm body
#==================================
from sextante.core.QGisLayers import QGisLayers
from qgis.core import *
from PyQt4.QtCore import *
from sextante.core.SextanteVectorWriter import SextanteVectorWriter
from scipy.spatial.distance import cdist
import numpy as np


# "input" contains the location of the selected layer.
# We get the actual object, so we can get its bounds
layer = QGisLayers.getObjectFromUri(input1)
provider = layer.dataProvider()
allAttrs = provider.attributeIndexes()
provider.select( allAttrs )
fields = provider.fields()
# add field for hausdorff distance
fields[len(fields)] = QgsField("HAUSDORFF", QVariant.Double)
writer = SextanteVectorWriter(output, None, fields, provider.geometryType(), provider.crs() )

inFeat = QgsFeature()
inFeat2 = QgsFeature()
outFeat = QgsFeature()
inGeom = QgsGeometry()
nFeat = provider.featureCount()

join_field1_index = provider.fieldNameIndex(join_field1)

# Create output vector layer with additional attribute
while provider.nextFeature(inFeat):
    inGeom = inFeat.geometry()
    atMap = inFeat.attributeMap()
    join_value1 = atMap[join_field1_index].toString()

    layer2 = QGisLayers.getObjectFromUri(input2)
    provider2 = layer2.dataProvider()
    allAttrs = provider2.attributeIndexes()
    provider2.select( allAttrs )
    join_field2_index = provider2.fieldNameIndex(join_field2)

    distances = []
    while provider2.nextFeature(inFeat2):
        inGeom2 = inFeat2.geometry()
        atMap2 = inFeat2.attributeMap()
        join_value2 = atMap2[join_field2_index].toString()
        if join_value1 != join_value2:
            continue
        D = cdist(inGeom.asPolyline(),inGeom2.asPolyline(),'euclidean')
        H1 = np.max(np.min(D, axis=1))
        H2 = np.max(np.min(D, axis=0))
        distances.append( max(H1,H2) )
        D = cdist(inGeom2.asPolyline(),inGeom.asPolyline(),'euclidean')
        H1 = np.max(np.min(D, axis=1))
        H2 = np.max(np.min(D, axis=0))
        distances.append( max(H1,H2) )

    hausdorff = max(distances)
    outFeat.setGeometry( inGeom )
    atMap = inFeat.attributeMap()
    outFeat.setAttributeMap( atMap )
    outFeat.addAttribute( len(provider.fields()), QVariant( float(hausdorff) ))
    writer.addFeature( outFeat )

del writer

