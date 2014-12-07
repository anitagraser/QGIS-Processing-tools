##Statistics=group
##layer1=vector
##field1=field layer1
##layer2=vector
##field2=field layer2
##t_test_results=output html

from qgis.core import *
import numpy as np
from scipy import stats 

layers = [layer1,layer2]
fields = [field1,field2]
values1 = []
values2 = []
values = [values1,values2]

for i in [0,1]:
    layer = processing.getObject(layers[i])
    provider = layer.dataProvider()
    field_index = layer.fieldNameIndex(fields[i])
    features = processing.features(layer)
    for feature in features:
        attributes = feature.attributes()
        value = attributes[field_index]
        if value:
            values[i].append(value)   

# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
(t_statistic,p_value) = stats.ttest_ind(values1,values2,equal_var=False)

print t_statistic
print p_value

# start writing html output
f = open(t_test_results, 'a')
html = "<p>T-test for two INDEPENDENT samples comparing %s %s and %s %s</p>" % (layer1,field1,layer2,field2)
html = html + "<TABLE>\n<tr><TH>Result  </TH> <TH>Value  </TH> </tr>"
html = html + "<tr><td>t-statistic</td><td>%f</td></tr>" % (t_statistic)
html = html + "<tr><td>p-value</td><td>%f (%s)</td></tr>" % (p_value,p_value)
html = html + "</table>"

f.write(html)
f.close
