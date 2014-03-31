from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

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
        ,entry_points = {
        'console_scripts': [
            'PsController = PsController.PsController:run'
        ]
    }
		)
