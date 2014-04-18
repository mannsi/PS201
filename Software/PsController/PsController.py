from tkinter.ttk import *
import logging
import tkinter.simpledialog

from PsController.Control.Controller import Controller
from PsController.UI.Dialogs.AboutDialog import *
from PsController.UI.Frames.SequenceTabFrame import SequenceTabFrame
from PsController.UI.Frames.StatusTabFrame import StatusTabFrame
import PsController.Utilities.OsHelper as osHelper
from PsController.UI.Controls.ToolTip import ToolTip

mainWindowSize = '650x400'
mainWindowTitle = "PS201 Controller"
controller = Controller()


class PsController():
    def __init__(self, debugging, forcedUsbPort):
        self.guiRefreshRate = 200
        self.mainWindow = Tk()
        systemType = osHelper.getCurrentOs()
        if systemType == osHelper.WINDOWS:
            img = Image("photo", file='electricity-24.gif')
        else:
            img = Image("photo", file='electricity-64.gif')
        self.mainWindow.tk.call('wm', 'iconphoto', self.mainWindow._w, img)

        self.mainWindow.title(mainWindowTitle)
        self.mainWindow.geometry(mainWindowSize)
        self.topPanel = _HeaderPanel(self.mainWindow)
        self.topPanel.pack(fill=X)
        self.tabControl = TabControl(self.mainWindow)
        self.tabControl.pack(fill=BOTH, expand=1)
        self.debugging = debugging
        self.forcedUsbPort = forcedUsbPort
        controller.forcedUsbPort = forcedUsbPort

        if self.debugging:
            if systemType == osHelper.WINDOWS:
                self.mainWindow.geometry('900x400')
            else:
                self.mainWindow.geometry('1100x400')
            debugFrame = Frame(self.mainWindow)

            self.btnDisconnect = Button(debugFrame, text="Disconnect", command=self.disconnectFromDevice,
                                        state=DISABLED)
            #self.btnDisconnect.pack(side=RIGHT)

            self.btnConnect = Button(debugFrame, text="Connect", command=self.connectToDevice)
            #self.btnConnect.pack(side=RIGHT)

            self.numOfRefreshPerSecVar = IntVar(value=2)
            self.numOfRefreshPerSec = Entry(debugFrame, textvariable=self.numOfRefreshPerSecVar, width=10)
            #self.numOfRefreshPerSec.pack(side=RIGHT)
            #Label(debugFrame, text="Refresh per sec").pack(side=RIGHT)

            self.updateTypeCmb = Combobox(debugFrame, values=["Polling", "Streaming"])
            #self.updateTypeCmb.pack(side=RIGHT)
            self.updateTypeCmb.current(newindex=1)
            #Label(debugFrame, text="Update type").pack(side=RIGHT)

            self.loggingCmb = Combobox(debugFrame, values=["Error", "Info", "Debug"])
            self.loggingCmb.bind("<<ComboboxSelected>>", self._logging_sel_changed)
            self.loggingCmb.pack(side=RIGHT)
            self.loggingCmb.current(newindex=1)
            Label(debugFrame, text="Logging").pack(side=RIGHT)
            self._logging_sel_changed(self.loggingCmb)

            self.btnUpdateAll = Button(debugFrame, text="Refresh", command=self.debugRefreshValues)
            #self.btnUpdateAll.pack(side=RIGHT)

            self.chkAutoVar = IntVar(value=1)
            self.chkAuto = Checkbutton(debugFrame, text="Auto update", variable=self.chkAutoVar,
                                       command=self.debugSwitchAutoMode)
            #self.chkAuto.pack(side=RIGHT)

            debugFrame.pack(fill=X)

        self.subMenu = None
        self.selectedUsbPortVar = StringVar()
        self.availableUsbPorts = []
        if not self.forcedUsbPort:
            controller.getAvailableUsbPorts(threaded=True)
            self.deviceUsbPort = None
        controller.getDeviceUsbPort(threaded=True, forcedUsbPort=self.forcedUsbPort)
        self.addMenuBar()
        controller.notifyConnectedUpdate(self.updateConnectedStatus)
        controller.notifyDeviceUsbPortUpdate(self.deviceUsbPortUpdate)
        controller.notifyUsbPortListUpdate(self.usbPortListUpdate)

    @staticmethod
    def debugRefreshValues():
        if controller.connected:
            controller._updateAllValuesWorker()

    def debugSwitchAutoMode(self):
        chkValue = self.chkAutoVar.get()
        if controller.connected:
            if chkValue:
                self.startAutoUpdate()
            else:
                controller.stopAutoUpdate()

    def updateConnectedStatus(self, value):
        connected = value[0]
        if connected:
            self.startAutoUpdate()
            if self.debugging:
                self.btnConnect.configure(state=DISABLED)
                self.btnDisconnect.configure(state=NORMAL)
        else:
            controller.stopAutoUpdate()
            if self.debugging:
                self.btnConnect.configure(state=NORMAL)
                self.btnDisconnect.configure(state=DISABLED)

    def startAutoUpdate(self):
        if self.debugging:
            if self.chkAutoVar.get():
                updateType = self.updateTypeCmb.current()
                controller.startAutoUpdate(interval=1 / self.numOfRefreshPerSecVar.get(), updateType=updateType)
        else:
            controller.startAutoUpdate(interval=1 / 2, updateType=1)

    def addMenuBar(self):
        menuBar = Menu(self.mainWindow)

        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=self.mainWindow.quit)

        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Tools", menu=toolsMenu)
        self.subMenu = Menu(toolsMenu, tearoff=0)
        self.buildUsbPortMenu()
        toolsMenu.add_cascade(label='Usb port', menu=self.subMenu, underline=0)

        editMenu = Menu(menuBar, tearoff=0)
        editMenu.add_command(label="About", command=self.showAboutDialog)
        menuBar.add_cascade(label="Help", menu=editMenu)

        self.mainWindow.config(menu=menuBar)

    def buildUsbPortMenu(self):
        self.subMenu.delete(0, END)

        if self.forcedUsbPort:
            self.subMenu.add_radiobutton(label=self.forcedUsbPort, value=self.forcedUsbPort, var=self.selectedUsbPortVar)
            self.selectedUsbPortVar.set(self.forcedUsbPort)
            self.usbPortSelected()
            return

        if self.deviceUsbPort and self.deviceUsbPort not in self.availableUsbPorts:
            self.availableUsbPorts.append(self.deviceUsbPort)

        if self.availableUsbPorts:
            for port in self.availableUsbPorts:
                self.subMenu.add_radiobutton(label=port, value=port, var=self.selectedUsbPortVar,
                                             command=self.usbPortSelected)
                if self.deviceUsbPort == port:
                    self.selectedUsbPortVar.set(port)
            self.subMenu.add_separator()
        self.subMenu.add_command(label="Refresh", command=self.buildUsbPortMenu)

    def usbPortSelected(self):
        if controller.connected:
            controller.disconnect()
        self.connectToDevice()

    def deviceUsbPortUpdate(self, port):
        self.deviceUsbPort = port
        self.buildUsbPortMenu()
        if port == "":
            # No port found for device so we start polling for device
            controller.pollForDeviceDevice()
        else:
            self.usbPortSelected()

    def usbPortListUpdate(self, usbPorts):
        self.availableUsbPorts = usbPorts
        self.buildUsbPortMenu()

    def showAboutDialog(self):
        AboutDialog(self.mainWindow, title="About", showCancel=False)

    def connectToDevice(self):
        usbPort = self.selectedUsbPortVar.get()
        controller.connect(usbPort, threaded=True)

    @staticmethod
    def disconnectFromDevice():
        controller.disconnect()

    def periodicUiUpdate(self):
        controller.uiPulse()
        self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)

    def _logging_sel_changed(self, widget):
        selectedIndex = self.loggingCmb.current()
        if selectedIndex == 0:
            controller.setLogging(logging.ERROR)
        elif selectedIndex == 1:
            controller.setLogging(logging.INFO)
        elif selectedIndex == 1:
            controller.setLogging(logging.DEBUG)

    def show(self):
        self.periodicUiUpdate()
        self.mainWindow.mainloop()


class _HeaderPanel(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        topLineFrame = Frame(self)

        self.chkOutputOnVar = IntVar(value=0)
        self.chkOutputOn = Checkbutton(topLineFrame, text="Output On", variable=self.chkOutputOnVar, state=DISABLED,
                                       command=self.outPutOnOff)
        self.chkOutputOn.grid(row=0, column=0)
        self.lblStatusValueVar = StringVar(value="Searching for device ...")
        Label(topLineFrame, textvariable=self.lblStatusValueVar).grid(row=0, column=1)
        self.lblConnectedImage = Label(topLineFrame)
        self.connectedImageToolTip = ToolTip(self.lblConnectedImage, msg="", delay=0.5)
        self.lblConnectedImage.grid(row=0, column=2)
        self.showConnectedState(False)

        topLineFrame.columnconfigure(1, weight=1)
        topLineFrame.pack(fill=X)

        self.valuesFrame = _ValuesFrame(self)
        self.valuesFrame.pack()
        controller.notifyConnectedUpdate(self.connectedUpdated)
        controller.notifyOutputUpdate(self.outPutOnOffUpdate)

    def outPutOnOff(self):
        chkValue = self.chkOutputOnVar.get()
        controller.setOutputOnOff(chkValue, threaded=True)

    def connectedUpdated(self, value):
        connected = value[0]
        self.showConnectedState(connected)

    def showConnectedState(self, connected):
        if connected:
            state = NORMAL
            connectedImage = Image("photo", file='green-circle-16.gif')
            toolTipMessage = "Connected"
            self.lblStatusValueVar.set("")
        else:
            state = DISABLED
            connectedImage = Image("photo", file='red-circle-16.gif')
            toolTipMessage = "Not connected"
            self.lblStatusValueVar.set("Searching for device ...")

        self.connectedImageToolTip.message(toolTipMessage)
        self.lblConnectedImage.configure(image=connectedImage)
        self.lblConnectedImage.img = connectedImage
        self.chkOutputOn.configure(state=state)

    def outPutOnOffUpdate(self, newOutputOn):
        self.chkOutputOnVar.set(newOutputOn == 1)


class _ValuesFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        fontName = "Verdana"
        fontSize = 20
        #Voltage
        Label(self, text="V", font=(fontName, fontSize)).grid(row=0, column=0)
        self.voltageEntryVar = DoubleVar(None)
        self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar, state='readonly', font=(fontName, fontSize),
                                  width=6, justify=RIGHT)
        self.voltageEntry.grid(row=0, column=1, sticky=W)
        Label(self, text="(V)").grid(row=0, column=2, sticky=W)
        self.btnSetTargetVoltage = Button(self, text="Set", state=DISABLED, command=self.setTargetVoltage, width=4)
        self.btnSetTargetVoltage.grid(row=0, column=3, sticky=N + S + E, pady=5)
        #Current
        Label(self, text="I", font=(fontName, fontSize)).grid(row=1, column=0)
        self.currentEntryVar = IntVar(None)
        self.currentEntry = Entry(self, textvariable=self.currentEntryVar, state='readonly', font=(fontName, fontSize),
                                  width=6, justify=RIGHT)
        self.currentEntry.grid(row=1, column=1, sticky=W)
        Label(self, text="(mA)").grid(row=1, column=2, sticky=W)
        self.btnSetTargetCurrent = Button(self, text="Set", state=DISABLED, command=self.setTargetCurrent, width=4)
        self.btnSetTargetCurrent.grid(row=1, column=3, sticky=N + S, pady=5)

        controller.notifyOutputCurrentUpdate(self.outputCurrentUpdate)
        controller.notifyOutputVoltageUpdate(self.outputVoltageUpdate)
        controller.notifyConnectedUpdate(self.connectedUpdated)

    def setTargetCurrent(self):
        targetCurrent = tkinter.simpledialog.askinteger("Current limit", "Enter new current limit (0-1000mA)",
                                                        parent=self)
        if targetCurrent is not None:
            if targetCurrent <= 1000:
                controller.setTargetCurrent(targetCurrent, threaded=True)

    def setTargetVoltage(self):
        targetVoltage = tkinter.simpledialog.askfloat("Target voltage", "Enter new target voltage (0.00 - 20.00 V)",
                                                      parent=self)
        if targetVoltage is not None:
            if 0 < targetVoltage <= 20:
                controller.setTargetVoltage(targetVoltage, threaded=True)

    def outputVoltageUpdate(self, newOutputVoltage):
        self.voltageEntryVar.set(newOutputVoltage)

    def outputCurrentUpdate(self, newOutputCurrent):
        self.currentEntryVar.set(int(newOutputCurrent))

    def connectedUpdated(self, value):
        connected = value[0]
        if connected:
            state = NORMAL
        else:
            state = DISABLED
        self.btnSetTargetCurrent.configure(state=state)
        self.btnSetTargetVoltage.configure(state=state)


class TabControl(Notebook):
    def __init__(self, parent):
        self.parent = parent
        Notebook.__init__(self, parent, name='tab control')

        self.statusTab = StatusTabFrame(self, controller)
        self.sequenceTab = SequenceTabFrame(self, self.resetSequenceTab, controller)

        self.add(self.statusTab, text='Status')
        self.add(self.sequenceTab, text='Sequence')

    def resetSequenceTab(self):
        self.forget(self.sequenceTab)
        self.sequenceTab = SequenceTabFrame(self, self.resetSequenceTab, controller)
        self.add(self.sequenceTab, text='Sequence')
        self.select(self.sequenceTab)


def run(isDebugMode, forcedUsbPort=None):
    psFrame = PsController(isDebugMode, forcedUsbPort)
    psFrame.show()


if __name__ == "__main__":
    run(False)
