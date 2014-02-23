@echo off
cd PsController
python createExe.py build
"C:\Program Files (x86)\Inno Setup 5\iscc" ..\PsController.iss
RMDIR build /S /Q



