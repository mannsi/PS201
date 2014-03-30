from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
"""
import sys	
platFormBase = "Console"
#For windows to hide the console window in the back
if (sys.platform == "win32"):
    platFormBase = "Win32GUI"
"""

setup(
        name = "PsController"
        ,version = "0.1"
        ,description = "PsController"
		,packages=find_packages()
        ,install_requires=[
			"APScheduler == 2.1.1",
			"crcmod == 1.7",
			"pyserial == 2.7"
]
	,scripts =["psControllerMain.py"]
        ,entry_points = {
        'console_scripts': [
            'PsController = psControllerMain:run'
        ]
    }
		)
