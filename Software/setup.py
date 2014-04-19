from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
import PsController.Utilities.OsHelper as osHelper

systemType = osHelper.getCurrentOs()

if systemType == osHelper.WINDOWS:
    dataFiles = ["Icons\\electricity-24.gif",
                 "Icons\\electricity-64.gif",
                 "Icons\\green-circle-16.gif",
                 "Icons\\green-circle-16.gif"]
else:
    dataFiles = ["Icons/electricity-24.gif",
                 "Icons/electricity-64.gif",
                 "Icons/green-circle-16.gif",
                 "Icons/green-circle-16.gif"]

setup(
    name="PsController"
    , version="0.1"
    , description="PsController"
    , packages=find_packages()
    , install_requires=[
        "APScheduler == 2.1.1",
        "crcmod == 1.7",
        "pyserial == 2.7"
    ]
    , scripts=["psControllerMain.py"]
    , data_files=[("Icons", dataFiles)]
    , entry_points={
        "console_scripts": [
            "PsController = psControllerMain:run"

        ]
    }
)
