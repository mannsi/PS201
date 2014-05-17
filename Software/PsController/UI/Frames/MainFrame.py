from tkinter.ttk import *
import logging
import tkinter.simpledialog

from ..Dialogs.AboutDialog import *
from ..Controls.ToolTip import ToolTip
from .TabControlFrame import TabControl
import PsController.Utilities.OsHelper as osHelper
import PsController.Utilities.IconHelper as iconHelper
import PsController.Model.Constants as Constants


mainWindowSize = '650x400'
mainWindowTitle = "PS201 Controller"


class MainFrame():
    def __init__(self, debugging, control):
        self.guiRefreshRate = 200
        self.mainWindow = Tk()
        self.setIcon()
        self.control = control

        # Set up main UI
        self.mainWindow.title(mainWindowTitle)
        self.mainWindow.geometry(mainWindowSize)
        self.topPanel = _TopFrame(self.mainWindow, self.control)
        self.topPanel.pack(fill=X)
        self.tabControl = TabControl(self.mainWindow, self.control)
        self.tabControl.pack(fill=BOTH, expand=1)

        # Create menu
        self.subMenu = None
        self.addMenuBar()

        if debugging:
            if osHelper.getCurrentOs() == osHelper.WINDOWS:
                self.mainWindow.geometry('900x400')
            else:
                self.mainWindow.geometry('1100x400')
            debugFrame = Frame(self.mainWindow)

            self.loggingCmb = Combobox(debugFrame, values=["Error", "Info", "Debug"])
            self.loggingCmb.bind("<<ComboboxSelected>>", self._logging_sel_changed)
            self.loggingCmb.pack(side=RIGHT)
            self.loggingCmb.current(newindex=1)
            Label(debugFrame, text="Logging").pack(side=RIGHT)
            self._logging_sel_changed(self.loggingCmb)
            debugFrame.pack(fill=X)

    def setIcon(self):
        self.mainWindow.tk.call(
            'wm', 'iconphoto', self.mainWindow._w,
            PhotoImage(data=iconHelper.getIconData('electricity-64.gif')))

    def addMenuBar(self):
        menuBar = Menu(self.mainWindow)

        fileMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=self.mainWindow.quit)

        editMenu = Menu(menuBar, tearoff=0)
        editMenu.add_command(label="About", command=self.showAboutDialog)
        menuBar.add_cascade(label="Help", menu=editMenu)

        self.mainWindow.config(menu=menuBar)

    def showAboutDialog(self):
        AboutDialog(self.mainWindow, title="About", showCancel=False)

    def periodicUiUpdate(self):
        self.control.uiPulse()
        self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)

    def _logging_sel_changed(self, widget):
        selectedIndex = self.loggingCmb.current()
        if selectedIndex == 0:
            self.control.setLogging(logging.ERROR)
        elif selectedIndex == 1:
            self.control.setLogging(logging.INFO)
        elif selectedIndex == 1:
            self.control.setLogging(logging.DEBUG)

    def show(self):
        self.periodicUiUpdate()
        self.mainWindow.mainloop()


class _TopFrame(Frame):
    """ The top part of the MainFrame. Contains connection check box, program status and connected state"""
    def __init__(self, parent, control):
        Frame.__init__(self, parent)
        self.parent = parent
        self.control = control

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

        self.valuesFrame = _OutputValuesFrame(self, self.control)
        self.valuesFrame.pack()
        self.control.notifyConnectedUpdate(self.connectedUpdated)
        self.control.notifyOutputUpdate(self.outPutOnOffUpdate)

    def outPutOnOff(self):
        chkValue = self.chkOutputOnVar.get()
        self.control.setOutputOnOff(chkValue)

    def connectedUpdated(self, value):
        connected = (value == Constants.CONNECTED)
        self.showConnectedState(connected)

    def showConnectedState(self, connected):
        if connected:
            state = NORMAL
            connectedImage = PhotoImage(data=iconHelper.getIconData('green-circle-16.gif'))
            toolTipMessage = "Connected"
            self.lblStatusValueVar.set("")
        else:
            state = DISABLED
            connectedImage = PhotoImage(data=iconHelper.getIconData('red-circle-16.gif'))
            toolTipMessage = "Not connected"
            self.lblStatusValueVar.set("Searching for device ...")

        self.connectedImageToolTip.message(toolTipMessage)
        self.lblConnectedImage.configure(image=connectedImage)
        self.lblConnectedImage.img = connectedImage
        self.chkOutputOn.configure(state=state)

    def outPutOnOffUpdate(self, newOutputOn):
        self.chkOutputOnVar.set(newOutputOn == 1)


class _OutputValuesFrame(Frame):
    """ Shows the output values of the DPS201. Also has buttons to set target values """
    def __init__(self, parent, control):
        Frame.__init__(self, parent)
        self.parent = parent
        self.control = control
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

        self.control.notifyOutputCurrentUpdate(self.outputCurrentUpdate)
        self.control.notifyOutputVoltageUpdate(self.outputVoltageUpdate)
        self.control.notifyConnectedUpdate(self.connectedUpdated)

    def setTargetCurrent(self):
        targetCurrent = tkinter.simpledialog.askinteger("Current limit", "Enter new current limit (0-1000mA)",
                                                        parent=self)
        if targetCurrent is not None:
            if targetCurrent <= 1000:
                self.control.setTargetCurrent(targetCurrent)

    def setTargetVoltage(self):
        targetVoltage = tkinter.simpledialog.askfloat("Target voltage", "Enter new target voltage (0.00 - 20.00 V)",
                                                      parent=self)
        if targetVoltage is not None:
            if 0 < targetVoltage <= 20:
                self.control.setTargetVoltage(targetVoltage)

    def outputVoltageUpdate(self, newOutputVoltage):
        self.voltageEntryVar.set(newOutputVoltage)

    def outputCurrentUpdate(self, newOutputCurrent):
        self.currentEntryVar.set(int(newOutputCurrent))

    def connectedUpdated(self, value):
        connected = (value == Constants.CONNECTED)
        if connected:
            state = NORMAL
        else:
            state = DISABLED
        self.btnSetTargetCurrent.configure(state=state)
        self.btnSetTargetVoltage.configure(state=state)