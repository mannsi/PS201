import os

runString = ""
if sys.platform == "win32":
  os.system("python setup.py bdist_msi")
else:
  print("Don't know how to create an install on linux")

