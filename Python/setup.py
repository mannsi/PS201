from cx_Freeze import setup, Executable
import sys

platFormBase = "Console"

# For windows to hide the console window in the back
#if (sys.platform == "win32"):
#    platFormBase = "Win32GUI"

executables = [
        Executable("ArduinoGUI.py", appendScriptToExe=True, appendScriptToLibrary=False, base=platFormBase)
]

buildOptions = dict(
        create_shared_zip = False)

setup(
        name = "ArduinoGUI",
        version = "0.1",
        description = "ArduinoGUI",
        options = dict(build_exe = buildOptions),
        executables = executables)