##Spatial statistics=group
##input=vector
##field=field input
##contiguity=selection queen;rook
##i=output number 

import pysal 
import numpy as np
import processing 
from processing.tools.vector import VectorWriter
from qgis.core import *
from PyQt4.QtCore import *

field = field[0:10] # try to handle Shapefile field length limit

if contiguity == 0: # queen
    print 'INFO: Local Moran\'s using queen contiguity'
    w=pysal.queen_from_shapefile(input)
else: # 1 for rook
    print 'INFO: Local Moran\'s using rook contiguity'
    w=pysal.rook_from_shapefile(input)
    
f = pysal.open(pysal.examples.get_path(input.replace('.shp','.dbf')))
y=np.array(f.by_col[str(field)])
m = pysal.Moran(y,w,transformation = "r", permutations = 999)

i=m.I

print "Moran's I: %f" % (m.I)
print "INFO: Moran's I values range from -1 (indicating perfect dispersion) to +1 (perfect correlation). Values close to -1/(n-1) indicate a random spatial pattern."
print "p_norm: %f" % (m.p_norm)
print "p_rand: %f" % (m.p_rand)
print "p_sim: %f" % (m.p_sim)
print "INFO: p values smaller than 0.05 indicate spatial autocorrelation that is significant at the 5% level."
print "z_norm: %f" % (m.z_norm)
print "z_rand: %f" % (m.z_rand)
print "z_sim: %f" % (m.z_sim)
print "INFO: z values greater than 1.96 or smaller than -1.96 indicate spatial autocorrelation that is significant at the 5% level."
