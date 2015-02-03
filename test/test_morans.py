import os, sys, glob
import unittest
import numpy as np

# Prepare the environment
from qgis.core import * # qgis.core must be imported before PyQt4.QtGui!!!
from PyQt4.QtGui import *
app = QApplication([])
QgsApplication.setPrefixPath("C:\\OSGeo4W64\\apps\\qgis",True)
QgsApplication.initQgis()

# Prepare processing framework 
sys.path.append( "C:\\OSGeo4W64\\apps\\qgis\\python\\plugins" ) 
from processing.core.Processing import Processing
from processing import runalg, alglist

class TestMorans(unittest.TestCase):
    def test_morans(self):
        Processing.initialize()
        np.random.seed(12345)
        alglist('moran')
        result = runalg("script:morans","C:/Users/anita_000/Documents/GitHub/QGIS-Processing-tools/test/data/stl_hom.shp","HR8893","rook")
        i = result['i']        
        self.assertEqual(i,0.24365582621771659)
        
if __name__ == '__main__':
    unittest.main()
    
