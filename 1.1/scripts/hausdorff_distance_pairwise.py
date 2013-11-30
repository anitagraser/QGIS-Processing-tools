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
from qgis.core import *
from PyQt4.QtCore import *
from processing.core.VectorWriter import VectorWriter
from scipy.spatial.distance import cdist
import numpy as np


# "input1" contains the location of the first input layer
layer = processing.getObject(input1)
provider = layer.dataProvider()
features = processing.features(layer)
fields = layer.pendingFields().toList()
join_field1_index = layer.fieldNameIndex(join_field1)
nFeat = layer.featureCount()

# "output" is the location of the output file
# we add field for hausdorff distance to the fields from input1
fields.append( QgsField("HAUSDORFF", QVariant.Double ))
writer = VectorWriter(output, None, fields, provider.geometryType(), layer.crs() )

inFeat = QgsFeature()
inFeat2 = QgsFeature()
outFeat = QgsFeature()
inGeom = QgsGeometry()



# Create output vector layer with additional attribute
for inFeat  in features:
    inGeom = inFeat.geometry()
    atMap = inFeat.attributes()
    join_value1 = str(atMap[join_field1_index])

    layer2 = processing.getObject(input2)
    features2 = processing.features(layer2)
    join_field2_index = layer2.fieldNameIndex(join_field2)

    distances = []
    for inFeat2 in features2:
        inGeom2 = inFeat2.geometry()
        atMap2 = inFeat2.attributes()
        join_value2 = str(atMap2[join_field2_index])
        if join_value1 != join_value2:
            continue
        # calculate distances between inGeom and inGeom2
        D = cdist(inGeom.asPolyline(),inGeom2.asPolyline(),'euclidean')
        H1 = np.max(np.min(D, axis=1))
        H2 = np.max(np.min(D, axis=0))
        distances.append( max(H1,H2) )
        # repeat the calculation in reverse order
        D = cdist(inGeom2.asPolyline(),inGeom.asPolyline(),'euclidean')
        H1 = np.max(np.min(D, axis=1))
        H2 = np.max(np.min(D, axis=0))
        distances.append( max(H1,H2) )

    hausdorff = max(distances)
    outFeat.setGeometry( inGeom )
    atMap = inFeat.attributes()
    atMap.append(float(hausdorff))
    outFeat.setAttributes( atMap )
    writer.addFeature( outFeat )

del writer
