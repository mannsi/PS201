# TODO
# Finish getOnOff function in controller
# Add the save to file func

from tkinter import *
from tkinter.ttk import *
import ThreadHelper
import PspController
import logging
"""
import matplotlib
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
"""
mainWindowSize = '550x300'
mainWindowTitle = "PSP200 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = PspController.Controller(loglevel = logging.DEBUG)
threadHelper = ThreadHelper.ThreadHelper(controller)

class Gui():
  def __init__(self):
    self.guiRefreshRate = 100
    self.deviceRefreshRate = 2000
    self.setAvailableUsbPorts()

  def connectToDevice(self, usbPort):
    self.periodicUiUpdate()
    if usbPort in self.avilableUsbPorts:
      usbPortNumber = self.avilableUsbPorts[usbPort]
    else:
      usbPortNumber = usbPort
    threadHelper.connect(usbPortNumber, self.onConnectToDevice)

  def setAvailableUsbPorts(self):
    self.avilableUsbPorts = controller.getAvailableUsbPorts()

  def onConnectToDevice(self):
    self.connected = True
    self.periodicValuesUpdate()

  def targetVoltageUpdate(self, targetVoltage):
    self.tabControl.ManualTab.voltageEntryVar.set(targetVoltage)

  def targetCurrentUpdate(self, targetCurrent):
    self.tabControl.ManualTab.currentEntryVar.set(targetCurrent)

  def realVoltageUpdate(self, realVoltage):
    self.topPanel.voltageFrame.voltageEntryVar.set(realVoltage)

  def realCurrentUpdate(self, realCurrent):
    self.topPanel.currntFrame.currentEntryVar.set(realCurrent)

  def outPutOnOffUpdate(self, shouldBeOn):
    self.topPanel.chkOutputOnVar.set(shouldBeOn)

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
    self.mainWindow = Tk()
    self.mainWindow.title(mainWindowTitle)
    self.mainWindow.pack_propagate(False) #Used to make sure the window does not resize to the child objects. Try to remove later
    self.mainWindow.geometry(mainWindowSize)
    self.topPanel = TopPanel(self.mainWindow, availableUsbPorts = self.avilableUsbPorts.keys())
    self.topPanel.pack(fill=X)
    self.tabControl = TabControl(self.mainWindow)
    self.tabControl.pack(fill=BOTH, expand=1)
    btnConnect = Button(self.mainWindow, text = "Connect", command = lambda: self.connectToDevice(self.topPanel.usbPort.get()))
    btnConnect.pack(side=RIGHT)
    inverseWidgetList.append(btnConnect)
    self.mainWindow.mainloop()

class TopPanel(Frame):
  def __init__(self, parent, availableUsbPorts):
    Frame.__init__(self, parent)
    self.parent = parent

    self.chkOutputOnVar = IntVar(value=0)
    self.chkOutputOn = Checkbutton(self, text = "Output On", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
    self.chkOutputOn.pack(side=LEFT, anchor=N)
    normalWidgetList.append(self.chkOutputOn)

    self.usbPort_value = StringVar()
    self.usbPort = Combobox(self, text="USB port: ", textvariable=self.usbPort_value)
    self.usbPort['values'] = ([x for x in availableUsbPorts])
    self.usbPort.current(0)
    self.usbPort.pack(side=RIGHT, anchor=N)
    inverseWidgetList.append(self.usbPort)
    lblUsbSelectText = Label(self, text="USB port: ").pack(side=RIGHT, anchor=N)

    statusPanel = Frame(self)
    self.lblStatus = Label(statusPanel, text="Status: ").pack(side=LEFT)
    self.lblStatusValueVar = StringVar(value="Not connected")
    self.lblStatusValue = Label(statusPanel, textvariable=self.lblStatusValueVar).pack(side=RIGHT)
    statusPanel.pack()

    self.voltageFrame = VoltageFrame(self)
    self.voltageFrame.pack()
    self.currentFrame = CurrentFrame(self)
    self.currentFrame.pack()

  def outPutOnOff(self):
    chkValue = self.chkOutputOnVar.get()
    controller.setOutputOnOff(chkValue)

class VoltageFrame(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar, state='readonly')
    self.voltageEntry.pack(side=RIGHT)
    Label(self, text="Output voltage:").pack(side=RIGHT)

class CurrentFrame(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.currentEntryVar = DoubleVar(None)
    self.currentEntry = Entry(self, textvariable=self.currentEntryVar, state='readonly')
    self.currentEntry.pack(side=RIGHT)
    self.currentLabel = Label(self, text="Output current:").pack(side=RIGHT)

class TabControl(Notebook):
  def __init__(self, parent):
    Notebook.__init__(self, parent, name='tab control 123')
    self.add(ManualTab(self), text='Manual')
    self.add(ScheduleTab(self), text='Schedule')
    self.add(Frame(), text='Graph')

class ManualTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    parent.ManualTab = self
    innerFrame = Frame(self)
    innerFrame.pack(fill=BOTH,expand=1, ipady=1, padx=10, pady=5)
    Label(innerFrame, text="Voltage").grid(row=0,column=0)
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(innerFrame, textvariable=self.voltageEntryVar)
    self.voltageEntry.grid(row=0, column=1)
    Label(innerFrame, text="Current").grid(row=1,column=0)
    self.currentEntryVar = DoubleVar(None)
    self.currentEntry = Entry(innerFrame, textvariable=self.currentEntryVar)
    self.currentEntry.grid(row=1, column=1)
    self.btnSetTargetCurrent = Button(innerFrame, text = "Set", state=DISABLED, command=self.setTargetCurrent)
    self.btnSetTargetCurrent.grid(row=1, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetCurrent)
    self.btnSetTargetVoltage = Button(innerFrame, text = "Set", state=DISABLED, command=self.setTargetVoltage)
    self.btnSetTargetVoltage.grid(row=0, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetVoltage)

  def setTargetCurrent(self):
    threadHelper.setTargetCurrent(self.currentEntryVar.get())

  def setTargetVoltage(self):
    threadHelper.setTargetVoltage(self.voltageEntryVar.get())

class ScheduleTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.addLinesFrame()

    buttonFrame = Frame(self)

    self.btnStart = Button(buttonFrame, text = "Start", state=DISABLED, command=self.start)
    self.btnStart.pack(side=LEFT)
    self.btnStop = Button(buttonFrame, text = "Stop", state=DISABLED, command=self.stop)
    self.btnStop.pack(side=LEFT)
    buttonFrame.pack()
    normalWidgetList.append(self.btnStart)

  def start(self):
    threadHelper.startSchedule(self.lines)
    self.btnStop.configure(state = NORMAL)
    self.btnStart.configure(state = DISABLED)

  def stop(self):
    threadHelper.stopSchedule()
    self.btnStart.configure(state = NORMAL)
    self.btnStop.configure(state = DISABLED)

  def addLinesFrame(self):
    linesFrameHub = Frame(self)
    self.linesFrame = Frame(linesFrameHub)
    Label(self.linesFrame, text="Voltage").grid(row=0,column=0,sticky=W)
    Label(self.linesFrame, text="Current").grid(row=0,column=1,sticky=W)
    Label(self.linesFrame, text="Duration").grid(row=0,column=2, columnspan=2,sticky=W)
    self.lines = []
    self.rowNumber = 1
    self.addLine()
    self.linesFrame.pack()
    self.btnAddLine = Button(linesFrameHub,text="+",width=3, command=self.addLine)
    self.btnAddLine.pack(anchor=E)
    linesFrameHub.pack()

  def addLine(self):
    line = ScheduleLine(self.linesFrame,self.rowNumber,self.removeLine)
    line.voltageEntry.grid(row=self.rowNumber,column=0)
    line.currentEntry.grid(row=self.rowNumber,column=1)
    line.timeSizeType.grid(row=self.rowNumber,column=2)
    line.durationEntry.grid(row=self.rowNumber,column=3)
    line.removeLineButton.grid(row=self.rowNumber,column=4)
    self.rowNumber += 1
    self.lines.append(line)

  def removeLine(self, rowNumber, listOfWidgets):
    for widget in listOfWidgets:
      widget.grid_forget()
    self.lines.pop(rowNumber-1)
    self.rowNumber -= 1

class ScheduleLine():
  def __init__(self, parent, rowNumber, removeLineFunc):
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(parent, textvariable=self.voltageEntryVar,width=10)
    self.currentEntryVar = DoubleVar(None)
    self.currentEntry = Entry(parent, textvariable=self.currentEntryVar,width=10)
    self.timeSizeType_value = StringVar()
    self.timeSizeType = Combobox(parent, textvariable=self.timeSizeType_value,state='readonly',width=7)
    self.timeSizeType['values'] = ('sec', 'min', 'hour')
    self.timeSizeType.current(0)
    self.durationEntryVar = DoubleVar(None)
    self.durationEntry = Entry(parent, textvariable=self.durationEntryVar,width=10)
    self.removeLineButton = Button(parent,text="-",width=3, command= lambda:removeLineFunc(rowNumber,[self.voltageEntry,self.currentEntry,self.timeSizeType,self.durationEntry,self.removeLineButton]))

"""
class ScheduleTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.addStartingValueFrame()
    self.addChangeLineFrame()
    self.addEveryXFrame()

    self.chkSaveToFileVar = IntVar(value=0)
    self.chkSaveToFile = Checkbutton(self, text = "Save results to file", variable = self.chkSaveToFileVar, state=DISABLED)
    self.chkSaveToFile.pack()

    self.btnStart = Button(self, text = "Start", state=DISABLED, command=self.btnStartClick)
    self.btnStart.pack()
    normalWidgetList.append(self.btnStart)

  def btnStartClick(self):
    # Check if values are ok

    stepSize = self.stepSizeVar.get()
    timeStepSize = self.timeSizeVar.get()

    if stepSize == 0 or timeStepSize == 0:
      print("illegal values")
      return
    startingVoltage = self.startVoltageEntryVar.get()
    startingCurrent = self.startCurrentEntryVar.get()
    changeType = self.changeType_value.get()
    plusMinus = self.plusMinus_value.get()
    timeType = self.timeSizeType_value.get()
    threadHelper.startScheduledJob(startingVoltage, startingCurrent, changeType, plusMinus, stepSize, timeStepSize, timeType)
    print("Starting volt: " , self.startVoltageEntryVar.get())
    print("Starting curr: " , self.startCurrentEntryVar.get())
    print("Changing unit: " , self.changeType_value.get())
    print("+/-: " , self.plusMinus_value.get())
    print("Step size: " , self.stepSizeVar.get())
    print("Time step size: " , self.timeSizeVar.get())
    print("Time step unit: " , self.timeSizeType_value.get())
    print("Save to file: " , self.chkSaveToFileVar.get())

  def addStartingValueFrame(self):
    startingFrame = Frame(self)
    startingFrame.pack(fill=X,ipady=1, padx=10, pady=5)
    Label(startingFrame, text="Starting voltage").grid(row=0,column=0)
    self.startVoltageEntryVar = DoubleVar(None)
    self.startVoltageEntry = Entry(startingFrame, textvariable=self.startVoltageEntryVar)
    self.startVoltageEntry.grid(row=0, column=1)
    Label(startingFrame, text="Starting current").grid(row=1,column=0)
    self.startCurrentEntryVar = DoubleVar(None)
    self.startCurrentEntry = Entry(startingFrame, textvariable=self.startCurrentEntryVar)
    self.startCurrentEntry.grid(row=1, column=1)

  def addChangeLineFrame(self):
    changeLine = Frame(self)
    changeLine.pack(side=TOP, anchor = W)
    Label(changeLine, text="Change").pack(side=LEFT)
    self.changeType_value = StringVar()
    changeType = Combobox(changeLine, textvariable=self.changeType_value, state='readonly', width = 7)
    changeType['values'] = ('voltage', 'current')
    changeType.current(0)
    changeType.pack(side=LEFT)
    Label(changeLine, text="by").pack(side=LEFT)
    self.plusMinus_value = StringVar()
    plusMinus = Combobox(changeLine, textvariable=self.plusMinus_value, state='readonly', width = 2)
    plusMinus['values'] = ('+', '-')
    plusMinus.current(0)
    plusMinus.pack(side=LEFT)
    self.stepSizeVar = DoubleVar(None)
    stepSize = Entry(changeLine, textvariable=self.stepSizeVar, width = 7)
    stepSize.pack(side=LEFT)
    normalWidgetList.append(stepSize)

  def addEveryXFrame(self):
    everyXLine = Frame(self)
    everyXLine.pack(side=TOP, anchor = W)
    Label(everyXLine, text="every").pack(side=LEFT)
    self.timeSizeVar = DoubleVar(None)
    self.timeSize = Entry(everyXLine, textvariable=self.timeSizeVar,width = 7)
    self.timeSize.pack(side=LEFT)

    self.timeSizeType_value = StringVar()
    timeSizeType = Combobox(everyXLine, textvariable=self.timeSizeType_value, state='readonly', width = 7)
    timeSizeType['values'] = ('sec', 'min', 'hour')
    timeSizeType.current(0)
    timeSizeType.pack(side=LEFT)
"""
if __name__ == "__main__":
  gui = Gui()
  gui.show()