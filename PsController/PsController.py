from tkinter import *
from tkinter.ttk import *
from Controller import Controller
import logging
import tkinter.simpledialog
from AboutDialog import *
from Dialogs import RampDialog, DataLoggingDialog
import tkBaseDialog
from SequenceLineFrame import *

mainWindowSize = '700x400'
mainWindowTitle = "PS201 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = Controller(shouldLog = True, loglevel = logging.ERROR)
targetVoltage = 0
targetCurrent = 0
inputVoltage = 0
realVoltage = 0
realCurrent = 0
outputOn = False
connectedPort = ''
selectedUsbPort = ''
connected = False

class PsFrame():
    def __init__(self):
      self.guiRefreshRate = 200
      self.mainWindow = Tk()
      self.mainWindow.title(mainWindowTitle)
      self.mainWindow.geometry(mainWindowSize)
      self.topPanel = HeaderPanel(self.mainWindow)
      self.topPanel.pack(fill=X)
      self.tabControl = TabControl(self.mainWindow)
      self.tabControl.pack(fill=BOTH, expand=1)
      btnConnect = Button(self.mainWindow, text = "Connect", command = lambda: self.connectToDevice(self.selectedUsbPort.get()))
      btnConnect.pack(side=RIGHT)
      inverseWidgetList.append(btnConnect)
      self.addMenuBar()
    
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
      self.selectedUsbPort = StringVar()
      if connectedPort != '' and connectedPort not in avilableUsbPorts:
        self.submenu.add_radiobutton(label=connectedPort,value=connectedPort,var=self.selectedUsbPort)
        self.selectedUsbPort.set(connectedPort)
      
      for port in avilableUsbPorts:
        self.submenu.add_radiobutton(label=port,value=port,var=self.selectedUsbPort)
        if defaultUsbPort == port:
          self.selectedUsbPort.set(port)
          
      self.submenu.add_separator()    
      self.submenu.add_command(label="Refresh", command=self.buildUsbPortMenu)
    
    def aboutDialog(self):
      dialog = AboutDialog(self.mainWindow,title="About",showCancel=False)
    
    def connectToDevice(self, usbPort):
      self.periodicUiUpdate()
      controller.connect(usbPort, threaded=True)
    
    def targetVoltageUpdate(self, newTargetVoltage):
      global targetVoltage
      targetVoltage = float(newTargetVoltage)
      self.tabControl.statusTab.voltageEntryVar.set(newTargetVoltage)

    def inputVoltageUpdate(self, newInputVoltage):
      global inputVoltage
      inputVoltage = float(newInputVoltage)
      self.tabControl.statusTab.voltageInputEntryVar.set(newInputVoltage)
    
    def targetCurrentUpdate(self, newTargetCurrent):
      global targetCurrent
      targetCurrent = int(newTargetCurrent)
      self.tabControl.statusTab.currentEntryVar.set(newTargetCurrent)
    
    def realVoltageUpdate(self, newRealVoltage):
      global realVoltage
      if newRealVoltage != realVoltage:
        realVoltage = newRealVoltage
        self.topPanel.valuesFrame.voltageEntryVar.set(newRealVoltage)
    
    def realCurrentUpdate(self, newRealCurrent):
      global realCurrent
      if newRealCurrent != realCurrent:
        realCurrent = newRealCurrent
        self.topPanel.valuesFrame.currentEntryVar.set(newRealCurrent)
    
    def outPutOnOffUpdate(self, newOutputOn):
      outputOn = bool(newOutputOn)
      self.topPanel.chkOutputOnVar.set(outputOn)
    
    def preRegVoltageUpdate(self, preRegVoltage):
      self.tabControl.statusTab.preRegVoltageEntryVar.set(preRegVoltage)
    
    def sequenceDone(self):
      self.tabControl.sequenceTab.selectLine(-1)  
      self.tabControl.sequenceTab.scheduleStopped()
      
    def sequenceLineChanged(self, rowNumber):
      self.tabControl.sequenceTab.selectLine(rowNumber)  
    
    """
    Periodically checks the queue for updates to the UI.
    """
    def periodicUiUpdate(self):
        while controller.queue.qsize():
            try:
                action = controller.queue.get(0)
                if action == PsController.connectString:
                    global connected
                    global connectedPort
                    connectStatus = controller.queue.get(0)
                    self.topPanel.lblStatusValueVar.set(connectStatus)
                    if connectStatus == PsController.connectedString:
                        connected = True
                        controller.startAutoUpdate(interval = 1)
                        connectedPort = controller.queue.get(0)
                        self.connectedStateChanged(True)
                    elif connectStatus == PsController.noDeviceFoundstr:
                        # When this state is reached I must stop listening more for this state since many thread will return this state
                        # I also have to stop the current threads until the connectedString is returned
                        connected = False
                        self.connectedStateChanged(False)  
                elif action == PsController.realCurrentString:
                    realCurrentValue = controller.queue.get(0)
                    self.realCurrentUpdate(realCurrentValue)
                elif action == PsController.realVoltageString:
                    realVoltageValue = controller.queue.get(0)
                    self.realVoltageUpdate(realVoltageValue)
                elif action == PsController.targetCurrentString:
                    targetCurrentValue = controller.queue.get(0)
                    self.targetCurrentUpdate(targetCurrentValue)
                elif action == PsController.targetVoltageString:
                    targetVoltageValue = controller.queue.get(0)
                    self.targetVoltageUpdate(targetVoltageValue)
                elif action == PsController.inputVoltageString:
                    inputVoltage = controller.queue.get(0)
                    self.inputVoltageUpdate(inputVoltage)
                elif action == PsController.outputOnOffString:
                    outputOnOff = controller.queue.get(0)
                    self.outPutOnOffUpdate(outputOnOff)
                elif action == PsController.preRegVoltageString:
                    preRegVoltageValue = controller.queue.get(0)
                    self.preRegVoltageUpdate(preRegVoltageValue)
                elif action == PsController.scheduleDoneString:
                    self.sequenceDone()
                elif action == PsController.scheduleNewLineString:
                    rowNumber = controller.queue.get(0)
                    self.sequenceLineChanged(rowNumber)
            except:
                pass
            finally:
                self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)
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

class HeaderPanel(Frame):
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
        
        self.valuesFrame = ValuesFrame(self)
        self.valuesFrame.pack(pady=10)
        
    def outPutOnOff(self):
        chkValue = self.chkOutputOnVar.get()
        controller.setOutputOnOff(chkValue, threaded=True)

class ValuesFrame(Frame):
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

class TabControl(Notebook):
    def __init__(self, parent):
        self.parent = parent
        Notebook.__init__(self, parent, name='tab control')
        
        self.statusTab = StatusTab(self)
        self.sequenceTab = SequenceTab(self,self.resetSequenceTab, False)
        
        self.add(self.statusTab, text='Status')
        self.add(self.sequenceTab, text='Sequence')
      
    def resetSequenceTab(self, connected): 
        self.forget(self.sequenceTab) 
        self.sequenceTab = SequenceTab(self,self.resetSequenceTab, connected)
        self.add(self.sequenceTab, text='Sequence')
        self.select(self.sequenceTab)

class StatusTab(Frame):
    def __init__(self, parent):
        Frame.__init__(self,parent)
        fontName = "Verdana"
        fontSize = 12
        
        Label(self, text="Target voltage:",font=(fontName, fontSize)).grid(row=0,column=0,sticky=E)
        self.voltageEntryVar = DoubleVar(None)
        self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.voltageEntry.grid(row=0, column=1)
        Label(self, text="(V):").grid(row=0,column=2,sticky=W)
        Label(self, text="Current limit:",font=(fontName, fontSize)).grid(row=1,column=0,sticky=E)
        self.currentEntryVar = IntVar(None)
        self.currentEntry = Entry(self, textvariable=self.currentEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.currentEntry.grid(row=1, column=1)
        Label(self, text="(mA):").grid(row=1,column=2,sticky=W)
        Label(self, text="Input voltage:",font=(fontName, fontSize)).grid(row=2,column=0,sticky=E)
        self.voltageInputEntryVar = DoubleVar(None)
        self.voltageInputEntry = Entry(self, textvariable=self.voltageInputEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.voltageInputEntry.grid(row=2, column=1)
        Label(self, text="(V):").grid(row=2,column=2,sticky=W)
        Label(self, text="Pre reg voltage:",font=(fontName, fontSize)).grid(row=3,column=0,sticky=E)
        self.preRegVoltageEntryVar = DoubleVar(None)
        self.preRegVoltageEntry = Entry(self, textvariable=self.preRegVoltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
        self.preRegVoltageEntry.grid(row=3, column=1)
        Label(self, text="(V):").grid(row=3,column=2,sticky=W)

class SequenceTab(Frame):
    def __init__(self, parent, resetTabM, connected):
        Frame.__init__(self,parent)
        self.parent = parent
        self.resetTabM = resetTabM
        self.initalizeView(connected)
    
    def initalizeView(self, connected):
        self.addLinesFrame()
        buttonFrame = Frame(self)
        self.btnAdd = Button(buttonFrame, text = "Add line", command=self.addLine)
        self.btnAdd.pack(side=LEFT)
        self.btnClearLines = Button(buttonFrame, text = "Clear", command=self.resetLines)
        self.btnClearLines.pack(side=LEFT)
        
        self.btnLinearRamping = Button(buttonFrame, text = "Linear ramping", command=self.linearRamping)
        self.btnLinearRamping.pack(side=LEFT)
        
        self.logToFileVar = IntVar(value=0)
        self.logToFile = Checkbutton(buttonFrame, text = "Log to file", variable = self.logToFileVar)
        self.logToFile.pack(side=LEFT)
        
        if connected:
            startButtonState = NORMAL
        else:
            startButtonState = DISABLED
        self.btnStop = Button(buttonFrame, text = "Stop", state=DISABLED, command=self.stop)
        self.btnStop.pack(side=RIGHT)
        self.btnStart = Button(buttonFrame, text = "Start", state=startButtonState, command=self.start)
        self.btnStart.pack(side=RIGHT)
        buttonFrame.pack(fill='x')
        normalWidgetList.append(self.btnStart) 
     
    def selectLine(self, rowNumber):
        self.sequenceLineFrame.selectLine(rowNumber)  
      
    def start(self):
        scheduleStarted = False
        if self.logToFileVar.get():
            dialog = DataLoggingDialog(self,title="Log to file")
            if dialog.okClicked:
                if dialog.logWhenValuesChange:
                    if dialog.filePath is not "":
                        scheduleStarted = controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                                    startingTargetVoltage = targetVoltage,
                                                                    startingTargetCurrent = targetCurrent, 
                                                                    startingOutputOn = outputOn,
                                                                    logWhenValuesChange=True,
                                                                    filePath=dialog.filePath)
                elif dialog.logEveryXSeconds:
                    if dialog.timeInterval:
                        scheduleStarted = controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                                     useLoggingTimeInterval=True,
                                                                     startingTargetVoltage = targetVoltage,
                                                                     startingTargetCurrent = targetCurrent, 
                                                                     startingOutputOn = outputOn,
                                                                     loggingTimeInterval=dialog.timeInterval,
                                                                     filePath=dialog.filePath)
        else:       
            scheduleStarted = controller.startSchedule(self.sequenceLineFrame.getLines(),
                                                         startingTargetVoltage = targetVoltage,
                                                         startingTargetCurrent = targetCurrent, 
                                                         startingOutputOn = outputOn)
        if (scheduleStarted):
            self.btnStop.configure(state = NORMAL)
            self.btnStart.configure(state = DISABLED)
            self.btnClearLines.configure(state = DISABLED)
            self.btnAdd.configure(state = DISABLED)
            self.btnLinearRamping.configure(state = DISABLED)
        
    def stop(self):
        controller.stopSchedule()
         
    def scheduleStopped(self):  
        self.btnStart.configure(state = NORMAL)
        self.btnClearLines.configure(state = NORMAL)
        self.btnAdd.configure(state = NORMAL)
        self.btnLinearRamping.configure(state = NORMAL)
        self.btnStop.configure(state = DISABLED)
      
    def addLine(self):
        self.sequenceLineFrame.addLine()
    
    def addLinesFrame(self):
        canvas = Canvas(self,height=100,highlightthickness=0)
        self.sequenceLineFrame = SequenceLineFrame(canvas)
        #self.scheduleLineFrame.pack(side=LEFT,anchor=N)
    
    def resetLines(self):
        self.resetTabM(connected)
    
    def linearRamping(self):
        dialog = RampDialog(self,title="Voltage ramp")
        if dialog.okClicked:
            for l in dialog.voltageRampLines:
                self.sequenceLineFrame.addLine(l.voltage,l.current,l.timeType,l.duration)

if __name__ == "__main__":
    psFrame = PsFrame()
    psFrame.show()