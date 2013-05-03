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


# Layer 1
layer = QGisLayers.getObjectFromUri(input1)
provider = layer.dataProvider()
allAttrs = provider.attributeIndexes()
provider.select( allAttrs )
fields = provider.fields()
join_field1_index = provider.fieldNameIndex(join_field1)
# Layer 2
layer2 = QGisLayers.getObjectFromUri(input2)
provider2 = layer2.dataProvider()
allAttrs = provider2.attributeIndexes()
provider2.select( allAttrs )
fields2 = provider2.fields()
join_field2_index = provider2.fieldNameIndex(join_field2)   

# Output
outFields = {}
for (i,f) in fields.iteritems():
    f.setName("a"+f.name())
    outFields[len(outFields)] = f
for (i,f) in fields2.iteritems():
    f.setName("b"+f.name())
    outFields[len(outFields)] = f
    
writer = SextanteVectorWriter(output, None, outFields, provider.geometryType(), provider.crs() )

inFeat = QgsFeature()
inFeat2 = QgsFeature()
outFeat = QgsFeature()

# Create output vector layer with additional attribute
while provider.nextFeature(inFeat):
    inGeom = inFeat.geometry()
    atMap = inFeat.attributeMap()
    join_value1 = atMap[join_field1_index].toString()

    while provider2.nextFeature(inFeat2):
        inGeom2 = inFeat2.geometry()
        atMap2 = inFeat2.attributeMap()
        join_value2 = atMap2[join_field2_index].toString()
        
        if join_value1 == join_value2:        
            # create the new feature
            outFeat.setGeometry( inGeom )
            outFeat.setAttributeMap( atMap )
            l = len(provider.fields())
            for (i,a) in atMap2.iteritems():             
                outFeat.addAttribute( l+i, a )                
    
            writer.addFeature( outFeat )

del writer
