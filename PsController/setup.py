from distutils.core import setup
import sys

#platFormBase = "Console"

# For windows to hide the console window in the back
#if (sys.platform == "win32"):
#    platFormBase = "Win32GUI"
"""
executables = [
        Executable("PsGui.py", appendScriptToExe=True, appendScriptToLibrary=False, base=platFormBase)
]

buildOptions = dict(
        create_shared_zip = False)
"""
setup(
        name = "PsController",
        version = "0.1",
        description = "PsController",
        options = dict(build_exe = buildOptions),
        executables = executables)

setup(name='PsController',
      version='1.0',
      description='Control software for the DPS201',
      author='Gudbjorn Einarsson',
      packages=['distutils', 'distutils.command'],
     )