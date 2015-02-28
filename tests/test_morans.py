# test based on the example found at
# http://pysal.readthedocs.org/en/latest/library/esda/moran.html#pysal.esda.moran.Moran

#>>> import pysal
#>>> w = pysal.open(pysal.examples.get_path("stl.gal")).read()
#>>> f = pysal.open(pysal.examples.get_path("stl_hom.txt"))
#>>> y = np.array(f.by_col['HR8893'])
#>>> mi = Moran(y,  w)
#>>> "%7.5f" % mi.I
#'0.24366'

from processing import runalg
import numpy as np
import pysal 

np.random.seed(12345)
result = runalg(
    "script:morans",
    pysal.examples.get_path("stl_hom.shp"),
    "HR8893",
    1 # for rook
    )
    
observed = round(result['i'],5)
desired = 0.24366#0.24365582621771659

try:
    np.testing.assert_equal(observed,desired)
except ValueError as e:
    e.message
else:
    print 'TEST INFO: everything is fine :)'

# this would be the code for headless testing:

#import os, sys, glob
#import unittest
#import numpy as np
#
## Prepare the environment
#from qgis.core import * # qgis.core must be imported before PyQt4.QtGui!!!
#from PyQt4.QtGui import *
#app = QApplication([])
#QgsApplication.setPrefixPath("C:\\OSGeo4W64\\apps\\qgis",True)
#QgsApplication.initQgis()
#
## Prepare processing framework 
#sys.path.append( "C:\\OSGeo4W64\\apps\\qgis\\python\\plugins" ) 
#from processing.core.Processing import Processing
#from processing import runalg, alglist
#
#class TestMorans(unittest.TestCase):
#    def test_morans(self):
#        Processing.initialize()
#        np.random.seed(12345)
#        alglist('moran')
#        result = runalg("script:morans","C:/Users/anita_000/Documents/GitHub/QGIS-Processing-tools/test/data/stl_hom.shp","HR8893","rook")
#        i = result['i']        
#        self.assertEqual(i,0.24365582621771659)
#        
#if __name__ == '__main__':
#    unittest.main()

