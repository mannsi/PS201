from cx_Freeze import setup, Executable
import PsController.Utilities.OsHelper as osHelper

platFormBase = "Console"
if osHelper.getCurrentOs() == osHelper.WINDOWS:
    platFormBase = "Win32GUI"  # For windows to hide the console window in the back

buildOptions = dict(include_files=['Icons/'])

setup(
    name="PsController"
    , version="0.1"
    , description="PsController"
    , options=dict(build_exe=buildOptions)
    , executables=[Executable("psControllerMain.py", base=platFormBase, targetName="PsController.exe")]
)
