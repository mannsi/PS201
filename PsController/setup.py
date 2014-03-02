from ez_setup import use_setuptools
use_setuptools()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
		,packages=installPackages
        ,install_requires=[
			"APScheduler == 2.1.1",
			"crcmod == 1.7",
			"pyserial == 2.7"
]
		)
