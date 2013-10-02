# TODO
# Finish getOnOff function in controller
from tkinter import *
from tkinter.ttk import *
import ThreadHelper
import PspController
import logging
import tkinter.simpledialog
from AboutDialog import *
from RampDialog import *
import tkBaseDialog
from ScheduleLineFrame import *
#from AutoScrollbarFrame import *

mainWindowSize = '700x400'
mainWindowTitle = "PSP200 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = PspController.Controller(shouldLog = True, loglevel = logging.DEBUG)
threadHelper = ThreadHelper.ThreadHelper(controller)

class Gui():
  def __init__(self):
    self.guiRefreshRate = 100
    self.deviceRefreshRate = 1000
    self.setAvailableUsbPorts()
    self.mainWindow = Tk()
    self.mainWindow.title(mainWindowTitle)
    self.mainWindow.geometry(mainWindowSize)
    self.topPanel = TopPanel(self.mainWindow, availableUsbPorts = [x for x in self.avilableUsbPorts.keys()], selectedPort = self.getTheLatestUsedUsbPort())
    self.topPanel.pack(fill=X)
    self.tabControl = TabControl(self.mainWindow)
    self.tabControl.pack(fill=BOTH, expand=1)
    btnConnect = Button(self.mainWindow, text = "Connect", command = lambda: self.connectToDevice(self.topPanel.usbPort.get()))
    btnConnect.pack(side=RIGHT)
    inverseWidgetList.append(btnConnect)
    self.addMenuBar()


  def addMenuBar(self):
    menubar = Menu(self.mainWindow)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=self.mainWindow.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="About",command=self.aboutDialog)
    #editmenu.add_separator()
    menubar.add_cascade(label="Help", menu=editmenu)

    self.mainWindow.config(menu=menubar)

  def aboutDialog(self):
    dialog = AboutDialog(self.mainWindow,title="About",showCancel=False)

  def connectToDevice(self, usbPort):
    self.periodicUiUpdate()
    if usbPort in self.avilableUsbPorts:
      usbPortNumber = self.avilableUsbPorts[usbPort]
    else:
      usbPortNumber = usbPort
    self.saveTheLastUsedUsbPort(usbPortNumber)
    threadHelper.connect(usbPortNumber, self.onConnectToDevice)

  def saveTheLastUsedUsbPort(self, usbPort):
    with open('usbPort.txt', 'w') as f:
      f.write(str(usbPort))

  def getTheLatestUsedUsbPort(self):
    try:
      with open('usbPort.txt', 'r') as f:
        lastUsbPortNumber = f.readline()
        for k,v in self.avilableUsbPorts.items():
          if str(v) == str(lastUsbPortNumber):
            return k
        else:
          return None
    except:
      return None

  def setAvailableUsbPorts(self):
    self.avilableUsbPorts = controller.getAvailableUsbPorts()

  def onConnectToDevice(self):
    self.connected = True
    self.periodicValuesUpdate()

  def targetVoltageUpdate(self, targetVoltage):
    self.tabControl.statusTab.voltageEntryVar.set(targetVoltage)

  def targetCurrentUpdate(self, targetCurrent):
    self.tabControl.statusTab.currentEntryVar.set(targetCurrent)

  def realVoltageUpdate(self, realVoltage):
    self.topPanel.valuesFrame.voltageEntryVar.set(realVoltage)

  def realCurrentUpdate(self, realCurrent):
    self.topPanel.valuesFrame.currentEntryVar.set(realCurrent)

  def outPutOnOffUpdate(self, shouldBeOn):
    self.topPanel.chkOutputOnVar.set(shouldBeOn)

  def preRegVoltageUpdate(self, preRegVoltage):
    self.tabControl.statusTab.preRegVoltageEntryVar.set(preRegVoltage)

  def scheduleDone(self):
    self.tabControl.scheduleTab.stop()

  """
  Periodically checks the threadHelper queue for updates to the UI.
  """
  def periodicUiUpdate(self):
    if threadHelper.queue.qsize():
      try:
        action = threadHelper.queue.get(0)
        if action == ThreadHelper.connectString:
          connectStatus = threadHelper.queue.get(0)
          self.topPanel.lblStatusValueVar.set(connectStatus)
          if connectStatus == ThreadHelper.connectedString:
            self.connectedStateChanged(True)
          elif connectStatus == noDeviceFoundstr:
            # When this state is reached I must stop listening more for this state since many thread will return this state
            # I also have to stop the current threads until the connectedString is returned
            print("periodic update UI no device found. Queue size ", threadHelper.queue.qsize())
            self.connected = False
            self.connectedStateChanged(False)

        elif action == ThreadHelper.realCurrentString:
          realCurrentValue = threadHelper.queue.get(0)
          self.realCurrentUpdate(realCurrentValue)
        elif action == ThreadHelper.realVoltageString:
          realVoltageValue = threadHelper.queue.get(0)
          self.realVoltageUpdate(realVoltageValue)
        elif action == ThreadHelper.targetCurrentString:
          targetCurrentValue = threadHelper.queue.get(0)
          self.targetCurrentUpdate(targetCurrentValue)
        elif action == ThreadHelper.targetVoltageString:
          targetVoltageValue = threadHelper.queue.get(0)
          self.targetVoltageUpdate(targetVoltageValue)
        elif action == ThreadHelper.outputOnOffString:
          outputOnOff = threadHelper.queue.get(0)
          self.outPutOnOffUpdate(outputOnOff)
        elif action == ThreadHelper.preRegVoltageString:
          preRegVoltageValue = threadHelper.queue.get(0)
          self.preRegVoltageUpdate(preRegVoltageValue)
        elif action == ThreadHelper.scheduleDoneString:
          self.scheduleDone()
      except:
        pass
      finally:
        self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)
    else:
      self.mainWindow.after(self.guiRefreshRate, self.periodicUiUpdate)

  """
  periodically asks the controller for new values. Done through the threadHelper. New values are
  stored in the threaHelper queue and fetched by another function
  """
  def periodicValuesUpdate(self):
    if self.connected:
        threadHelper.updateCurrentAndVoltage()
        self.mainWindow.after(self.deviceRefreshRate, self.periodicValuesUpdate)

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

class TopPanel(Frame):
  def __init__(self, parent, availableUsbPorts, selectedPort = None):
    Frame.__init__(self, parent)
    self.parent = parent

    topLinFrame = Frame(self)
    self.selectedPort = selectedPort
    self.chkOutputOnVar = IntVar(value=0)
    self.chkOutputOn = Checkbutton(topLinFrame, text = "Output On", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
    self.chkOutputOn.pack(side=LEFT, anchor=N)
    normalWidgetList.append(self.chkOutputOn)

    self.usbPort_value = StringVar()
    self.usbPort = Combobox(topLinFrame, text="USB port: ", textvariable=self.usbPort_value)
    self.usbPort['values'] = ([x for x in availableUsbPorts])
    if selectedPort:
      self.usbPort.current(availableUsbPorts.index(selectedPort))
    else:
      self.usbPort.current(0)
    self.usbPort.pack(side=RIGHT, anchor=N)
    inverseWidgetList.append(self.usbPort)
    lblUsbSelectText = Label(topLinFrame, text="USB port: ").pack(side=RIGHT, anchor=N)
    self.usbPort.bind("<Button-1>", self.comboBoxDropDown)

    statusPanel = Frame(topLinFrame)
    self.lblStatus = Label(statusPanel, text="Status: ").pack(side=LEFT)
    self.lblStatusValueVar = StringVar(value="Not connected")
    self.lblStatusValue = Label(statusPanel, textvariable=self.lblStatusValueVar).pack(side=RIGHT)
    statusPanel.pack()
    topLinFrame.pack(fill=X)

    self.valuesFrame = ValuesFrame(self)
    self.valuesFrame.pack(pady=10)
 
  def comboBoxDropDown(self,event): 
    self.usbPort['values'] = [x for x in controller.getAvailableUsbPorts().keys()]
    
  def outPutOnOff(self):
    chkValue = self.chkOutputOnVar.get()
    controller.setOutputOnOff(chkValue)

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
    targetCurrent = tkinter.simpledialog.askinteger("Target current", "Enter new target current",parent=self)
    if targetCurrent is not None:
      threadHelper.setTargetCurrent(targetCurrent)

  def setTargetVoltage(self,args=None):
    targetVoltage = tkinter.simpledialog.askfloat("Target voltage", "Enter new target voltage",parent=self)
    if targetVoltage is not None:
      threadHelper.setTargetVoltage(targetVoltage)

class TabControl(Notebook):
  def __init__(self, parent):
    self.parent = parent
    Notebook.__init__(self, parent, name='tab control')
    
    self.statusTab = StatusTab(self)
    self.scheduleTab = ScheduleTab(self,self.resetScheduleTab)
    
    self.add(self.statusTab, text='Status')
    self.add(self.scheduleTab, text='Schedule')
    #self.add(ExamplesTab(self), text='Examples')
    
  def resetScheduleTab(self): 
      self.forget(self.scheduleTab) 
      self.scheduleTab = ScheduleTab(self,self.resetScheduleTab)
      self.add(self.scheduleTab, text='Schedule')
      self.select(self.scheduleTab)
    
class ExamplesTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    ex1 = Example(self,"Simple voltage increment", "A simple example that increments the voltage periodically and saves the results to file")
    ex1.pack(pady=10)
    ex2 = Example(self,"(Non)Destructive LED testing", "Here Frissi will have to both accept the example and give me a description to put here")
    ex2.pack(pady=10)
    ex3 = Example(self,"LiPo battery charging", "Here Frissi will have to both accept the example and give me a description to put here")
    ex3.pack()

# TODO add button and make less ugly
class Example(Frame):
  def __init__(self,parent,title,text):
    Frame.__init__(self,parent)
    Label(self, text=title).pack()
    Label(self, text=text).pack()


class StatusTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    parent.statusTab = self
    fontName = "Verdana"
    fontSize = 12

    Label(self, text="Target voltage:",font=(fontName, fontSize)).grid(row=0,column=0,sticky=E)
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
    self.voltageEntry.grid(row=0, column=1)
    Label(self, text="(V):").grid(row=0,column=2,sticky=W)
    Label(self, text="Target current:",font=(fontName, fontSize)).grid(row=1,column=0,sticky=E)
    self.currentEntryVar = IntVar(None)
    self.currentEntry = Entry(self, textvariable=self.currentEntryVar,width=8,state='readonly',font=(fontName, fontSize))
    self.currentEntry.grid(row=1, column=1)
    Label(self, text="(mA):").grid(row=1,column=2,sticky=W)
    Label(self, text="Pre reg voltage:",font=(fontName, fontSize)).grid(row=2,column=0,sticky=E)
    self.preRegVoltageEntryVar = DoubleVar(None)
    self.preRegVoltageEntry = Entry(self, textvariable=self.preRegVoltageEntryVar,width=8,state='readonly',font=(fontName, fontSize))
    self.preRegVoltageEntry.grid(row=2, column=1)
    Label(self, text="(V):").grid(row=2,column=2,sticky=W)

class ScheduleTab(Frame):
  def __init__(self, parent, resetTabM):
    Frame.__init__(self,parent)
    parent.scheduleTab = self
    self.parent = parent
    self.resetTabM = resetTabM
    self.initalizeView()

  def initalizeView(self):
    self.addLinesFrame()
    buttonFrame = Frame(self)
    self.btnAdd = Button(buttonFrame, text = "Add line", command=self.addLine)
    self.btnAdd.pack(side=LEFT)
    self.btnClearLines = Button(buttonFrame, text = "Clear", command=self.resetLines)
    self.btnClearLines.pack(side=LEFT)

    self.btnVoltageRamping = Button(buttonFrame, text = "Voltage ramping", command=self.voltageRamping)
    self.btnVoltageRamping.pack(side=LEFT)
    self.btnCurrentRamping = Button(buttonFrame, text = "Current ramping", command=self.currentRamping)
    self.btnCurrentRamping.pack(side=LEFT)

    self.btnStop = Button(buttonFrame, text = "Stop", state=DISABLED, command=self.stop)
    self.btnStop.pack(side=RIGHT)
    self.btnStart = Button(buttonFrame, text = "Start", state=DISABLED, command=self.start)
    self.btnStart.pack(side=RIGHT)
    buttonFrame.pack(fill='x')
    normalWidgetList.append(self.btnStart)
    
  def start(self):
    threadHelper.startSchedule(self.scheduleLineFrame.getLines())
    self.btnStop.configure(state = NORMAL)
    self.btnStart.configure(state = DISABLED)

  def stop(self):
    threadHelper.stopSchedule()
    self.btnStart.configure(state = NORMAL)
    self.btnStop.configure(state = DISABLED)

  def addLine(self):
    self.scheduleLineFrame.addLine()

  def addLinesFrame(self):
    canvas = Canvas(self,height=100,highlightthickness=0)
    self.scheduleLineFrame = ScheduleLineFrame(canvas)
    #self.scheduleLineFrame.pack(side=LEFT,anchor=N)

  def resetLines(self):
    self.resetTabM()

  def voltageRamping(self):
    dialog = RampDialog(self,title="Voltage ramp",type="VoltageRamp")
    if dialog.okClicked:
        for l in dialog.voltageRampLines:
          self.scheduleLineFrame.addLine(l.voltage,l.current,l.timeType,l.duration)

  def currentRamping(self):
    dialog = RampDialog(self,title="Current ramp",type = "CurrentRamp")
    if dialog.okClicked:
        for l in dialog.currentRampLines:
          self.scheduleLineFrame.addLine(l.voltage,l.current,l.timeType,l.duration)

if __name__ == "__main__":
  gui = Gui()
  gui.show()