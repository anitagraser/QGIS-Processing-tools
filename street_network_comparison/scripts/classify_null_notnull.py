#Definition of inputs and outputs
#==================================
##[my scripts]=group
##input=vector
##class_field=field input
##output=output vector

#Algorithm body
#==================================
from sextante.core.QGisLayers import QGisLayers
from qgis.core import *
from PyQt4.QtCore import *
from sextante.core.SextanteVectorWriter import SextanteVectorWriter

layer = QGisLayers.getObjectFromUri(input)
provider = layer.dataProvider()
allAttrs = provider.attributeIndexes()
provider.select( allAttrs )
fields = provider.fields()
class_field_index = provider.fieldNameIndex(class_field)

# Output
outFields = fields
outFields[len(outFields)] = QgsField("HASVALUE", QVariant.Int)    
writer = SextanteVectorWriter(output, None, outFields, provider.geometryType(), provider.crs() )

inFeat = QgsFeature()
outFeat = QgsFeature()

# Create output vector layer with additional attribute
while provider.nextFeature(inFeat):
    inGeom = inFeat.geometry()
    
    outFeat.setGeometry( inGeom )
    atMap = inFeat.attributeMap()
    class_value = atMap[class_field_index].toString()
    
    outFeat.setAttributeMap( atMap )
    outFeat.addAttribute( len(provider.fields()), QVariant( int( class_value != '' ) ))
    writer.addFeature( outFeat )

del writer
