#Definition of inputs and outputs
#==================================
##[my scripts]=group
##input=vector
##dividend=field input
##divisor=field input
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
dividend_field_index = provider.fieldNameIndex(dividend)
divisor_field_index = provider.fieldNameIndex(divisor)

# Output
outFields = fields
outFields[len(outFields)] = QgsField("RATIO", QVariant.Double)    
writer = SextanteVectorWriter(output, None, outFields, provider.geometryType(), provider.crs() )

inFeat = QgsFeature()
outFeat = QgsFeature()

# Create output vector layer with additional attribute
while provider.nextFeature(inFeat):
    inGeom = inFeat.geometry()
    
    outFeat.setGeometry( inGeom )
    atMap = inFeat.attributeMap()
    dividend = float(atMap[dividend_field_index].toString())
    divisor = float(atMap[divisor_field_index].toString())
    
    outFeat.setAttributeMap( atMap )
    if divisor != 0:
        outFeat.addAttribute( len(provider.fields()), QVariant( dividend/divisor ))
    else:
        outFeat.addAttribute( len(provider.fields()), QVariant( None ))
    writer.addFeature( outFeat )

del writer
