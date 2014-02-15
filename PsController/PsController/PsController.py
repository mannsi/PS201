from tkinter import *
from tkinter.ttk import *
from Control.Controller import Controller
import Control.Controller
import logging
import os
import tkinter.simpledialog
from UI.Dialogs.AboutDialog import *
from UI.Frames.SequenceTabFrame import SequenceTabFrame
from UI.Frames.StatusTabFrame import StatusTabFrame
from Model.DeviceValues import DeviceValues

mainWindowSize = '700x400'
mainWindowTitle = "PS201 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = Controller(shouldLog = True, loglevel = logging.ERROR)
currentValues = DeviceValues()

class PsController():
    def __init__(self):
      self.guiRefreshRate = 200
      self.mainWindow = Tk()
      self.mainWindow.title(mainWindowTitle)
      self.mainWindow.geometry(mainWindowSize)
      self.topPanel = _HeaderPanel(self.mainWindow)
      self.topPanel.pack(fill=X)
      self.tabControl = TabControl(self.mainWindow)
      self.tabControl.pack(fill=BOTH, expand=1)
      btnConnect = Button(self.mainWindow, text = "Connect", command = lambda: self.connectToDevice())
      btnConnect.pack(side=RIGHT)
      inverseWidgetList.append(btnConnect)
      self.addMenuBar()
      controller.registerUpdateFunction(self.updateConnectedStatus, Control.Controller.connectUpdate)
      controller.registerUpdateFunction(self.realCurrentUpdate, Control.Controller.realCurrentUpdate)
      controller.registerUpdateFunction(self.realVoltageUpdate, Control.Controller.realVoltageUpdate)
      controller.registerUpdateFunction(self.targetCurrentUpdate, Control.Controller.targetCurrentUpdate)
      controller.registerUpdateFunction(self.targetVoltageUpdate, Control.Controller.targetVoltageUpdate)
      controller.registerUpdateFunction(self.inputVoltageUpdate, Control.Controller.inputVoltageUpdate)
      controller.registerUpdateFunction(self.outPutOnOffUpdate, Control.Controller.outputOnOffUpdate)
      controller.registerUpdateFunction(self.preRegVoltageUpdate, Control.Controller.preRegVoltageUpdate)
    
    def updateConnectedStatus(self, value):
        if value == Control.Controller.connectedString:
            controller.startAutoUpdate(interval = 1)
            self.connectedStateChanged(True)
        elif value == Control.Controller.noDeviceFoundstr:
            self.connectedStateChanged(False)  

    def addMenuBar(self):
      menubar = Menu(self.mainWindow)
    
      fileMenu = Menu(menubar, tearoff=0)
      menubar.add_cascade(label="File", menu=fileMenu)
      fileMenu.add_command(label="Exit", command=self.mainWindow.quit)
      
      toolsMenu = Menu(menubar, tearoff=0)
      menubar.add_cascade(label="Tools", menu=toolsMenu)
      self.submenu = Menu(toolsMenu,tearoff=0)
      self.buildUsbPortMenu()
      toolsMenu.add_cascade(label='Usb port', menu=self.submenu, underline=0)
      
      editmenu = Menu(menubar, tearoff=0)
      editmenu.add_command(label="About",command=self.aboutDialog)
      menubar.add_cascade(label="Help", menu=editmenu)
    
      self.mainWindow.config(menu=menubar)
    
    def buildUsbPortMenu(self):
      self.submenu.delete(0, END)
      (avilableUsbPorts, defaultUsbPort) = controller.getAvailableUsbPorts()
      self.selectedUsbPortVar = StringVar()
      for port in avilableUsbPorts:
        self.submenu.add_radiobutton(label=port,value=port,var=self.selectedUsbPortVar)
        if defaultUsbPort == port:
          self.selectedUsbPortVar.set(port)
          
      self.submenu.add_separator()    
      self.submenu.add_command(label="Refresh", command=self.buildUsbPortMenu)
    
    def aboutDialog(self):
      dialog = AboutDialog(self.mainWindow,title="About",showCancel=False)
    
    def connectToDevice(self):
        usbPort = self.selectedUsbPortVar.get()
        self.periodicUiUpdate()
        controller.connect(usbPort, threaded=True)
    
    def targetVoltageUpdate(self, newTargetVoltage):
        global currentValues
        currentValues.targetVoltage = float(newTargetVoltage)

    def inputVoltageUpdate(self, newInputVoltage):
        global currentValues
        currentValues.inputVoltage = float(newInputVoltage)
    
    def targetCurrentUpdate(self, newTargetCurrent):
        global currentValues
        currentValues.targetCurrent = int(newTargetCurrent)
    
    def realVoltageUpdate(self, newRealVoltage):
        global currentValues
        currentValues.realVoltage = newRealVoltage
    
    def realCurrentUpdate(self, newRealCurrent):
        global currentValues
        currentValues.realCurrent = newRealCurrent
    
    def outPutOnOffUpdate(self, newOutputOn):
        global currentValues
        currentValues.outputOn = newOutputOn
    
    def preRegVoltageUpdate(self, preRegVoltage):
        global currentValues
        currentValues.preRegVoltage = preRegVoltage
    
    def periodicUiUpdate(self):
        controller.uiPulse()
        self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)

    def connectedStateChanged(self, connected):
        if connected:
            state = NORMAL
            inverseState = DISABLED
        else:
            state = DISABLED
            inverseState = NORMAL
       
        for widget in normalWidgetList:
            widget.configure(state=state)
       
        for widget in inverseWidgetList:
            widget.configure(state=inverseState)
    
    def show(self):
        self.mainWindow.mainloop()

class _HeaderPanel(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        
        topLinFrame = Frame(self)
        self.chkOutputOnVar = IntVar(value=0)
        self.chkOutputOn = Checkbutton(topLinFrame, text = "Output On", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
        self.chkOutputOn.pack(side=LEFT, anchor=N)
        normalWidgetList.append(self.chkOutputOn)
        Label(topLinFrame, text="", width=15).pack(side=RIGHT, anchor=N)
        statusPanel = Frame(topLinFrame)
        self.lblStatus = Label(statusPanel, text="Status: ").pack(side=LEFT)
        self.lblStatusValueVar = StringVar(value="Not connected")
        self.lblStatusValue = Label(statusPanel, textvariable=self.lblStatusValueVar).pack()
        statusPanel.pack()
        topLinFrame.pack(fill=X)
        self.valuesFrame = _ValuesFrame(self)
        self.valuesFrame.pack(pady=10)
        controller.registerUpdateFunction(self.updateConnectionStatus, Control.Controller.connectUpdate)
        controller.registerUpdateFunction(self.outPutOnOffUpdate, Control.Controller.outputOnOffUpdate)

    def outPutOnOff(self):
        chkValue = self.chkOutputOnVar.get()
        controller.setOutputOnOff(chkValue, threaded=True)

    def updateConnectionStatus(self, value):
        connectStatus = value
        self.lblStatusValueVar.set(connectStatus)

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
        normalWidgetList.append(self.btnSetTargetVoltage)
        #Current
        Label(self, text="I", font=(fontName, fontSize)).grid(row=1,column=0)
        self.currentEntryVar = IntVar(None)
        self.currentEntry = Entry(self, textvariable=self.currentEntryVar,state='readonly',font=(fontName, fontSize),width=6,justify=RIGHT)
        self.currentEntry.grid(row=1,column=1,sticky=W)
        Label(self, text="(mA)").grid(row=1,column=2,sticky=W)
        self.btnSetTargetCurrent = Button(self,text="Set",state=DISABLED,command=self.setTargetCurrent,width=4)
        self.btnSetTargetCurrent.grid(row=1,column=3,sticky=N+S,pady=5)
        normalWidgetList.append(self.btnSetTargetCurrent)

        controller.registerUpdateFunction(self.realCurrentUpdate, Control.Controller.realCurrentUpdate)
        controller.registerUpdateFunction(self.realVoltageUpdate, Control.Controller.realVoltageUpdate)

    
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

    def realVoltageUpdate(self, newRealVoltage):
        self.voltageEntryVar.set(newRealVoltage)
    
    def realCurrentUpdate(self, newRealCurrent):
        self.currentEntryVar.set(newRealCurrent)

class TabControl(Notebook):
    def __init__(self, parent):
        self.parent = parent
        Notebook.__init__(self, parent, name='tab control')
        
        self.statusTab = StatusTabFrame(self, controller)
        self.sequenceTab = SequenceTabFrame(self,self.resetSequenceTab, False, controller, normalWidgetList)
        
        self.add(self.statusTab, text='Status')
        self.add(self.sequenceTab, text='Sequence')
      
    def resetSequenceTab(self, connected): 
        self.forget(self.sequenceTab) 
        self.sequenceTab = SequenceTab(self,self.resetSequenceTab, connected)
        self.add(self.sequenceTab, text='Sequence')
        self.select(self.sequenceTab)

if __name__ == "__main__":
    psFrame = PsController()
    psFrame.connectToDevice()
    psFrame.show()

    
