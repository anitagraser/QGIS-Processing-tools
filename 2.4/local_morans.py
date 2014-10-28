##Spatial statistics=group
##input=vector
##field=field input
##morans_output=output vector

import pysal 
import numpy as np
import processing 
from processing.core.VectorWriter import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *

layer = processing.getObject(input)
provider = layer.dataProvider()
fields = provider.fields()
fields.append(QgsField('MORANS_P', QVariant.Double))
fields.append(QgsField('MORANS_Q', QVariant.Int))
writer = VectorWriter(morans_output, None,fields, provider.geometryType(), layer.crs() )

w=pysal.rook_from_shapefile(input)
f = pysal.open(pysal.examples.get_path(input.replace('.shp','.dbf')))
y=np.array(f.by_col[str(field)])
lm = pysal.Moran_Local(y,w)
print lm.p_sim
print lm.q
# github.com/pysal/pysal/blob/master/pysal/esda/moran.py
# values indicate quadrat location 1 HH,  2 LH,  3 LL,  4 HL
# http://www.biomedware.com/files/documentation/spacestat/Statistics/LM/Results/Interpreting_univariate_Local_Moran_statistics.htm
# category - scatter plot quadrant - autocorrelation - interpretation
# high-high - upper right (red) - positive - Cluster - "I'm high and my neighbors are high."
# high-low - lower right (pink) - negative - Outlier - "I'm a high outlier among low neighbors."
# low-low - lower left (med. blue) - positive - Cluster - "I'm low and my neighbors are low."
# low-high - upper left (light blue) - negative - Outlier - "I'm a low outlier among high neighbors."

outFeat = QgsFeature()
i = 0
for inFeat in processing.features(layer):
    inGeom = inFeat.geometry()
    outFeat.setGeometry(inGeom)
    attrs = inFeat.attributes()
    attrs.append(float(lm.p_sim[i]))
    attrs.append(int(lm.q[i]))
    outFeat.setAttributes(attrs)
    writer.addFeature(outFeat)
    i+=1

del writer
