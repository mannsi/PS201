
from PsController.Control.Control import Control
from PsController.UI.Frames.MainFrame import MainFrame
from PsController.DAL.DAL import DAL


def run(isDebugMode, forcedUsbPort=None):
    control = Control(DAL=DAL(), threaded=True)
    control.connect(forcedUsbPort=forcedUsbPort)
    mainFrame = MainFrame(isDebugMode, control)
    mainFrame.show()


if __name__ == "__main__":
    run(False)
