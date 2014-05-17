
from PsController.Control.Controller import Controller
from PsController.UI.Frames.MainFrame import MainFrame
from PsController.Model.Model import Model


def run(isDebugMode, forcedUsbPort=None):
    control = Controller(Model=Model(), threaded=True)
    control.connect(forcedUsbPort=forcedUsbPort)
    mainFrame = MainFrame(isDebugMode, control)
    mainFrame.show()


if __name__ == "__main__":
    run(False)
