from tkinter import *
from tkinter.ttk import *
import logging
import os
import tkinter.simpledialog
from PsController.Control.Controller import Controller
from PsController.UI.Dialogs.AboutDialog import *
from PsController.UI.Frames.SequenceTabFrame import SequenceTabFrame
from PsController.UI.Frames.StatusTabFrame import StatusTabFrame

mainWindowSize = '800x400'
mainWindowTitle = "PS201 Controller"

controller = Controller()

class PsController():
    def __init__(self, debugging):
        self.guiRefreshRate = 200
        self.mainWindow = Tk()
        self.mainWindow.title(mainWindowTitle)
        self.mainWindow.geometry(mainWindowSize)
        self.topPanel = _HeaderPanel(self.mainWindow)
        self.topPanel.pack(fill=X)
        self.tabControl = TabControl(self.mainWindow)
        self.tabControl.pack(fill=BOTH, expand=1)
        self.debugging = debugging

        if self.debugging:
            debugFrame = Frame(self.mainWindow)

            self.numOfRefreshPerSecVar = IntVar(value=2)
            self.numOfRefreshPerSec = Entry(debugFrame, textvariable=self.numOfRefreshPerSecVar, width=10)
            self.numOfRefreshPerSec.pack(side=RIGHT)
            Label(debugFrame, text="Refresh per sec").pack(side=RIGHT)
        
            self.updateTypeCmb = Combobox(debugFrame,values=["Polling","Streaming"])
            self.updateTypeCmb.pack(side=RIGHT)
            self.updateTypeCmb.current(newindex=0)
            Label(debugFrame, text="Update type").pack(side=RIGHT)

            self.loggingCmb = Combobox(debugFrame, values=["Error","Details"])
            self.loggingCmb.bind("<<ComboboxSelected>>", self._logging_sel_changed)
            self.loggingCmb.pack(side=RIGHT)
            self.loggingCmb.current(newindex=0)
            Label(debugFrame, text="Logging").pack(side=RIGHT)

            self.btnUpdateAll = Button(debugFrame, text = "Refresh", command = self.debugRefreshValues)
            self.btnUpdateAll.pack(side=RIGHT)

            self.chkAutoVar = IntVar(value=0)
            self.chkAuto = Checkbutton(debugFrame, text = "Auto update", variable = self.chkAutoVar, command = self.debugSwitchAutoMode)
            self.chkAuto.pack(side=RIGHT)

            debugFrame.pack(fill=X)

        self.btnConnect = Button(self.mainWindow, text = "Connect", command = self.connectToDevice)
        self.btnConnect.pack(side=RIGHT)

        self.addMenuBar()
        controller.notifyConnectedUpdate(self.updateConnectedStatus)
        controller.notifyDefaultUsbPortUpdate(self.defaultPortUpdate)
    
    def debugRefreshValues(self):
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
            if self.chkAutoVar.get():
                self.startAutoUpdate()
            state = DISABLED
        else:
            state = NORMAL

        self.btnConnect.configure(state=state)
        if self.debugging:
            self.numOfRefreshPerSec.configure(state=state)
            self.updateTypeCmb.configure(state=state)

    def startAutoUpdate(self):
        if self.debugging:
                type = self.updateTypeCmb.current()
                controller.startAutoUpdate(interval = 1/self.numOfRefreshPerSecVar.get(), updateType=type)
        else:
            pass
            controller.startAutoUpdate(interval = 1/3, updateType=0)

    def addMenuBar(self):
        menubar = Menu(self.mainWindow)
    
        fileMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Exit", command=self.mainWindow.quit)
      
        toolsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=toolsMenu)
        self.submenu = Menu(toolsMenu,tearoff=0)
        self.buildUsbPortMenu(threaded=True)
        toolsMenu.add_cascade(label='Usb port', menu=self.submenu, underline=0)
      
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="About",command=self.aboutDialog)
        menubar.add_cascade(label="Help", menu=editmenu)
    
        self.mainWindow.config(menu=menubar)

    def buildUsbPortMenu(self, threaded=False):
        self.submenu.delete(0, END)
        availableUsbPorts = controller.getAvailableUsbPorts()
        defaultUsbPort = controller.getDeviceUsbPort(availableUsbPorts, threaded)
        self.selectedUsbPortVar = StringVar()
        for port in availableUsbPorts:
            self.submenu.add_radiobutton(label=port,value=port,var=self.selectedUsbPortVar)
            if defaultUsbPort == port:
                self.selectedUsbPortVar.set(port)
                break     
        self.submenu.add_separator()    
        self.submenu.add_command(label="Refresh", command=self.buildUsbPortMenu)
    
    def defaultPortUpdate(self, port):
        self.selectedUsbPortVar.set(port)

    def aboutDialog(self):
        dialog = AboutDialog(self.mainWindow,title="About",showCancel=False)
    
    def connectToDevice(self):
        usbPort = self.selectedUsbPortVar.get()
        controller.connect(usbPort, threaded=True)
      
    def periodicUiUpdate(self):
        controller.uiPulse()
        self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)
    
    def _logging_sel_changed(self, widget):
        selectedIndex = self.loggingCmb.current()
        if selectedIndex == 0:
            controller.setLogging(logging.ERROR)
        elif selectedIndex == 1:
            controller.setLogging(logging.DEBUG)

    def show(self):
        self.periodicUiUpdate()
        self.mainWindow.mainloop()

class _HeaderPanel(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        
        topLinFrame = Frame(self)
        self.chkOutputOnVar = IntVar(value=0)
        self.chkOutputOn = Checkbutton(topLinFrame, text = "Output On", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
        self.chkOutputOn.pack(side=LEFT, anchor=N)
        Label(topLinFrame, text="", width=15).pack(side=RIGHT, anchor=N)
        statusPanel = Frame(topLinFrame)
        self.lblStatus = Label(statusPanel, text="Status: ").pack(side=LEFT)
        self.lblStatusValueVar = StringVar(value="Not connected")
        self.lblStatusValue = Label(statusPanel, textvariable=self.lblStatusValueVar).pack()
        statusPanel.pack()
        topLinFrame.pack(fill=X)
        self.valuesFrame = _ValuesFrame(self)
        self.valuesFrame.pack(pady=10)
        controller.notifyConnectedUpdate(self.connectedUpdated)
        controller.notifyOutputUpdate(self.outPutOnOffUpdate)

    def outPutOnOff(self):
        chkValue = self.chkOutputOnVar.get()
        controller.setOutputOnOff(chkValue, threaded=True)

    def connectedUpdated(self, value):
        connected = value[0]
        connectedString = value[1]
        if connected:
            state = NORMAL
        else:
            state = DISABLED
        self.chkOutputOn.configure(state=state)
        self.lblStatusValueVar.set(connectedString)

    def outPutOnOffUpdate(self, newOutputOn):
        self.chkOutputOnVar.set(newOutputOn == 1)

class _ValuesFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self,parent)
        self.parent=parent
        fontName = "Verdana"
        fontSize = 20
        #Voltage
        Label(self, text="V", font=(fontName, fontSize)).grid(row=0,column=0)
        self.voltageEntryVar = DoubleVar(None)
        self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar, state='readonly',font=(fontName, fontSize),width=6,justify=RIGHT)
        self.voltageEntry.grid(row=0,column=1,sticky=W)
        Label(self, text="(V)").grid(row=0,column=2,sticky=W)
        self.btnSetTargetVoltage = Button(self,text="Set",state=DISABLED,command=self.setTargetVoltage,width=4)
        self.btnSetTargetVoltage.grid(row=0,column=3,sticky=N+S+E,pady=5)
        #Current
        Label(self, text="I", font=(fontName, fontSize)).grid(row=1,column=0)
        self.currentEntryVar = IntVar(None)
        self.currentEntry = Entry(self, textvariable=self.currentEntryVar,state='readonly',font=(fontName, fontSize),width=6,justify=RIGHT)
        self.currentEntry.grid(row=1,column=1,sticky=W)
        Label(self, text="(mA)").grid(row=1,column=2,sticky=W)
        self.btnSetTargetCurrent = Button(self,text="Set",state=DISABLED,command=self.setTargetCurrent,width=4)
        self.btnSetTargetCurrent.grid(row=1,column=3,sticky=N+S,pady=5)

        controller.notifyOutputCurrentUpdate(self.outputCurrentUpdate)
        controller.notifyOutputVoltageUpdate(self.outputVoltageUpdate)
        controller.notifyConnectedUpdate(self.connectedUpdated)
    
    def setTargetCurrent(self,args=None):
        targetCurrent = tkinter.simpledialog.askinteger("Current limit", "Enter new current limit (0-1000mA)",parent=self)
        if targetCurrent is not None:
            if(targetCurrent <= 1000):
                controller.setTargetCurrent(targetCurrent, threaded=True)
          
    def setTargetVoltage(self,args=None):
        targetVoltage = tkinter.simpledialog.askfloat("Target voltage", "Enter new target voltage (0.00 - 20.00 V)",parent=self)
        if targetVoltage is not None:
            if (targetVoltage > 0 and targetVoltage <= 20):
                controller.setTargetVoltage(targetVoltage, threaded=True)        

    def outputVoltageUpdate(self, newOutputVoltage):
        self.voltageEntryVar.set(newOutputVoltage)
    
    def outputCurrentUpdate(self, newOutputCurrent):
        self.currentEntryVar.set(newOutputCurrent)

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
        self.sequenceTab = SequenceTabFrame(self,self.resetSequenceTab, False, controller)
        
        self.add(self.statusTab, text='Status')
        self.add(self.sequenceTab, text='Sequence')
      
    def resetSequenceTab(self, connected): 
        self.forget(self.sequenceTab) 
        self.sequenceTab = SequenceTabFrame(self,self.resetSequenceTab, False, controller)
        self.add(self.sequenceTab, text='Sequence')
        self.select(self.sequenceTab)

def run(isDebugMode):
    psFrame = PsController(isDebugMode)
    #psFrame.connectToDevice()
    psFrame.show()

if __name__ == "__main__":
    run(False)

    
