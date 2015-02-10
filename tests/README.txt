Since headless testing does not seem to work yet, we do test in the QGIS Python Console.

Open the test script in the Python Console Editor and run it.

Notes
-----

Once headless testing of Processing scripts works, you can do the following:

On Windows, use the OSGeo4W shell and execute:

set PYTHONPATH=c:\OSGeo4W64\apps\qgis\python
set PATH=c:\OSGeo4W64\apps\qgis\bin;%PATH%

Then you can run the test Python scripts

python test_morans.py
