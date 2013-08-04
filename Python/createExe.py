import os
import sys

runString = ""
if sys.platform == "win32":
  runString = "python setup.py build"
else:
  runString = "python3 setup.py build"

os.system(runString)
