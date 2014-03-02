from cx_Freeze import setup, Executable
import sys

platFormBase = "Console"

#For windows to hide the console window in the back
if (sys.platform == "win32"):
    platFormBase = "Win32GUI"

installPackages = ['PsController'
		,'PsController.Control'
		,'PsController.DAL'
		,'PsController.Model'
		,'PsController.UI.Controls'
		,'PsController.UI.Dialogs'
		,'PsController.UI.Frames'
		,'PsController.Utilities'
		]

setup(
        name = "PsController"
        ,version = "0.1"
        ,description = "PsController"
		#,packages=installPackages
        ,executables = [Executable("PsController.py" , base=platFormBase)]
		)
