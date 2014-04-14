from cx_Freeze import setup, Executable
import sys

platFormBase = "Console"
if sys.platform == "win32":
    platFormBase = "Win32GUI"  # For windows to hide the console window in the back

setup(
    name="PsController"
    , version="0.1"
    , description="PsController"
    , executables=[Executable("psControllerMain.py", base=platFormBase, targetName="PsController.exe")]
)
