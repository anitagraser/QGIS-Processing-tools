##Spatial statistics=group
##input=vector
##field=field input
##contiguity=selection queen;rook
##morans_output=output vector

import pysal 
import numpy as np
import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *

# np.random.seed(10)

field = field[0:10] # try to handle Shapefile field length limit

layer = processing.getObject(input)
provider = layer.dataProvider()
fields = provider.fields()
fields.append(QgsField('MORANS_P', QVariant.Double))
fields.append(QgsField('MORANS_Z', QVariant.Double))
fields.append(QgsField('MORANS_Q', QVariant.Int))
fields.append(QgsField('MORANS_I', QVariant.Double))
fields.append(QgsField('MORANS_C', QVariant.Double))
writer = VectorWriter(morans_output, None,fields, provider.geometryType(), layer.crs() )

if contiguity == 0: # queen
    print 'INFO: Local Moran\'s using queen contiguity'
    w=pysal.queen_from_shapefile(input)
else: # 1 for rook
    print 'INFO: Local Moran\'s using rook contiguity'
    w=pysal.rook_from_shapefile(input)

f = pysal.open(pysal.examples.get_path(input.replace('.shp','.dbf')))
y=np.array(f.by_col[str(field)])
lm = pysal.Moran_Local(y,w,transformation = "r", permutations = 999)

# http://pysal.readthedocs.org/en/latest/library/esda/moran.html?highlight=local%20moran#pysal.esda.moran.Moran_Local
# values indicate quadrat location 1 HH,  2 LH,  3 LL,  4 HL

# http://www.biomedware.com/files/documentation/spacestat/Statistics/LM/Results/Interpreting_univariate_Local_Moran_statistics.htm
# category - scatter plot quadrant - autocorrelation - interpretation
# high-high - upper right (red) - positive - Cluster - "I'm high and my neighbors are high."
# high-low - lower right (pink) - negative - Outlier - "I'm a high outlier among low neighbors."
# low-low - lower left (med. blue) - positive - Cluster - "I'm low and my neighbors are low."
# low-high - upper left (light blue) - negative - Outlier - "I'm a low outlier among high neighbors."

# http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#/What_is_a_z_score_What_is_a_p_value/005p00000006000000/
# z-score (Standard Deviations) | p-value (Probability) | Confidence level
#     < -1.65 or > +1.65        |        < 0.10         |       90%
#     < -1.96 or > +1.96        |        < 0.05         |       95%
#     < -2.58 or > +2.58        |        < 0.01         |       99%


sig_q = lm.q * (lm.p_sim <= 0.01) # could make significance level an option
outFeat = QgsFeature()
i = 0
for inFeat in processing.features(layer):
    inGeom = inFeat.geometry()
    outFeat.setGeometry(inGeom)
    attrs = inFeat.attributes()
    attrs.append(float(lm.p_sim[i]))
    attrs.append(float(lm.z_sim[i]))
    attrs.append(int(lm.q[i]))
    attrs.append(float(lm.Is[i]))
    attrs.append(int(sig_q[i]))
    outFeat.setAttributes(attrs)
    writer.addFeature(outFeat)
    i+=1

del writer
