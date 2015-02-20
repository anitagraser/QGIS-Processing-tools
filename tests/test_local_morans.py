# test based on the example found at
# http://pysal.readthedocs.org/en/latest/users/tutorials/autocorrelation.html#local-moran-s-i

from processing import runalg
import numpy as np
import pysal 

np.random.seed(12345)
result = runalg(
    "script:localmorans",
    pysal.examples.get_path("stl_hom.shp"),
    "HR8893",
    "rook",
    None)

result_layer = processing.load(result['morans_output'])
p = []
for f in result_layer.getFeatures():
    p.append(f['MORANS_P'])
    
observed = p

desired = [ 0.176,  0.073,  0.405,  0.267,  0.332,  0.057,  0.296,  0.242,
        0.055,  0.062,  0.273,  0.488,  0.44 ,  0.354,  0.415,  0.478,
        0.473,  0.374,  0.415,  0.21 ,  0.161,  0.025,  0.338,  0.375,
        0.285,  0.374,  0.208,  0.3  ,  0.373,  0.411,  0.478,  0.414,
        0.009,  0.429,  0.269,  0.015,  0.005,  0.002,  0.077,  0.001,
        0.088,  0.459,  0.435,  0.365,  0.231,  0.017,  0.033,  0.04 ,
        0.068,  0.101,  0.284,  0.309,  0.113,  0.457,  0.045,  0.269,
        0.118,  0.346,  0.328,  0.379,  0.342,  0.39 ,  0.376,  0.467,
        0.357,  0.241,  0.26 ,  0.401,  0.185,  0.172,  0.248,  0.4  ,
        0.482,  0.159,  0.373,  0.455,  0.083,  0.128]
try:
    np.testing.assert_equal(observed,desired)
except ValueError as e:
    e.message
else:
    print 'TEST INFO: everything is fine :)'