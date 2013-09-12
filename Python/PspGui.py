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
mainWindowSize = '800x400'
mainWindowTitle = "PSP200 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = PspController.Controller(shouldLog = True, loglevel = logging.DEBUG)
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
    self.topPanel.valuesFrame.targetVoltageVar.set("Target: %s" % (targetVoltage))

  def targetCurrentUpdate(self, targetCurrent):
    self.topPanel.valuesFrame.targetCurrentVar.set("Target: %s" % (targetCurrent))

  def realVoltageUpdate(self, realVoltage):
    self.topPanel.valuesFrame.voltageEntryVar.set(realVoltage)

  def realCurrentUpdate(self, realCurrent):
    self.topPanel.valuesFrame.currentEntryVar.set(realCurrent)

  def outPutOnOffUpdate(self, shouldBeOn):
    self.topPanel.chkOutputOnVar.set(shouldBeOn)

  def preRegVoltageUpdate(self, preRegVoltage):
    self.topPanel.valuesFrame.preRegVoltageVar.set("PreReg: %s" % (preRegVoltage))

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

    topLinFrame = Frame(self)
    self.chkOutputOnVar = IntVar(value=0)
    self.chkOutputOn = Checkbutton(topLinFrame, text = "Output On", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
    self.chkOutputOn.pack(side=LEFT, anchor=N)
    normalWidgetList.append(self.chkOutputOn)

    self.usbPort_value = StringVar()
    self.usbPort = Combobox(topLinFrame, text="USB port: ", textvariable=self.usbPort_value)
    self.usbPort['values'] = ([x for x in availableUsbPorts])
    self.usbPort.current(0)
    self.usbPort.pack(side=RIGHT, anchor=N)
    inverseWidgetList.append(self.usbPort)
    lblUsbSelectText = Label(topLinFrame, text="USB port: ").pack(side=RIGHT, anchor=N)

    statusPanel = Frame(topLinFrame)
    self.lblStatus = Label(statusPanel, text="Status: ").pack(side=LEFT)
    self.lblStatusValueVar = StringVar(value="Not connected")
    self.lblStatusValue = Label(statusPanel, textvariable=self.lblStatusValueVar).pack(side=RIGHT)
    statusPanel.pack()
    topLinFrame.pack(fill=X)

    self.valuesFrame = ValuesFrame(self)
    self.valuesFrame.pack(pady=10)

  def outPutOnOff(self):
    chkValue = self.chkOutputOnVar.get()
    controller.setOutputOnOff(chkValue)

class ValuesFrame(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    fontName = "Courier New"
    fontSize = 30
    #Voltage
    Label(self, text="V:", font=(fontName, fontSize)).grid(row=0,column=0)
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar, state='readonly',font=(fontName, fontSize),width=6,justify=RIGHT)
    self.voltageEntry.grid(row=0,column=1,sticky=W)
    Label(self, text="(V)").grid(row=0,column=2,sticky=W)
    self.targetVoltageVar = StringVar()
    Label(self, textvariable=self.targetVoltageVar).grid(row=0,column=3,sticky=W)
    self.preRegVoltageVar = StringVar()
    Label(self, textvariable=self.preRegVoltageVar).grid(row=0,column=4,sticky=W)
    #Current
    Label(self, text="I:", font=(fontName, fontSize)).grid(row=1,column=0)
    self.currentEntryVar = IntVar(None)
    self.currentEntry = Entry(self, textvariable=self.currentEntryVar,state='readonly',font=(fontName, fontSize),width=6,justify=RIGHT)
    self.currentEntry.grid(row=1,column=1,sticky=W)
    Label(self, text="(mA)").grid(row=1,column=2,sticky=W)
    self.targetCurrentVar = StringVar()
    Label(self, textvariable=self.targetCurrentVar).grid(row=1,column=3,sticky=W)

class TabControl(Notebook):
  def __init__(self, parent):
    Notebook.__init__(self, parent, name='tab control 123')
    self.add(ManualTab(self), text='Manual')
    self.add(ScheduleTab(self), text='Schedule')

class ManualTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    parent.ManualTab = self
    Label(self, text="Target voltage(V):").grid(row=0,column=0,sticky=E)
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar,width=10)
    self.voltageEntry.grid(row=0, column=1)
    Label(self, text="Target current(mA):").grid(row=1,column=0,sticky=E)
    self.currentEntryVar = IntVar(None)
    self.currentEntry = Entry(self, textvariable=self.currentEntryVar,width=10)
    self.currentEntry.grid(row=1, column=1)
    self.btnSetTargetCurrent = Button(self, text = "Set", state=DISABLED, command=self.setTargetCurrent)
    self.btnSetTargetCurrent.grid(row=1, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetCurrent)
    self.btnSetTargetVoltage = Button(self, text = "Set", state=DISABLED, command=self.setTargetVoltage)
    self.btnSetTargetVoltage.grid(row=0, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetVoltage)

  def setTargetCurrent(self):
    threadHelper.setTargetCurrent(self.currentEntryVar.get())

  def setTargetVoltage(self):
    threadHelper.setTargetVoltage(self.voltageEntryVar.get())

class ScheduleTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.innerFrame = Frame(self)
    self.addLinesFrame()
    buttonFrame = Frame(self.innerFrame)
    self.btnStart = Button(buttonFrame, text = "Start", state=DISABLED, command=self.start)
    self.btnStart.pack(side=LEFT)
    self.btnStop = Button(buttonFrame, text = "Stop", state=DISABLED, command=self.stop)
    self.btnStop.pack(side=LEFT)
    buttonFrame.pack()
    normalWidgetList.append(self.btnStart)
    self.innerFrame.pack(side=LEFT, anchor=N)

  def start(self):
    threadHelper.startSchedule(self.lines)
    self.btnStop.configure(state = NORMAL)
    self.btnStart.configure(state = DISABLED)

  def stop(self):
    threadHelper.stopSchedule()
    self.btnStart.configure(state = NORMAL)
    self.btnStop.configure(state = DISABLED)

  def addLinesFrame(self):
    linesFrameHub = Frame(self.innerFrame)
    self.linesFrame = Frame(linesFrameHub)
    Label(self.linesFrame, text="Voltage(V)").grid(row=0,column=0,sticky=W)
    Label(self.linesFrame, text="Current(mA)").grid(row=0,column=1,sticky=W)
    Label(self.linesFrame, text="Duration").grid(row=0,column=2, columnspan=2)
    self.lines = []
    self.rowNumber = 1
    self.addLine()
    self.linesFrame.pack()
    self.btnAddLine = Button(linesFrameHub,text="+",width=3, command=self.addLine)
    self.btnAddLine.pack(anchor=E)
    linesFrameHub.pack()

  def addLine(self):
    if self.rowNumber == 1:
      line = ScheduleLine(self.linesFrame,self.rowNumber,self.removeLine)
    else:
      prevLine = self.lines[self.rowNumber - 2]
      print(prevLine.getVoltage())
      print(prevLine.getCurrent())
      print(prevLine.getTimeType())
      print(prevLine.getDuration())
      line = ScheduleLine(self.linesFrame,self.rowNumber,self.removeLine,voltage=prevLine.getVoltage(),current=prevLine.getCurrent(),timeType=prevLine.getTimeType(),duration=prevLine.getDuration())

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
  def __init__(self, parent, rowNumber, removeLineFunc, voltage=0, current=0, timeType='sec', duration=0):
    self.voltageEntryVar = DoubleVar(None)
    self.voltageEntryVar.set(voltage)
    self.voltageEntry = Entry(parent, textvariable=self.voltageEntryVar,width=10)
    self.currentEntryVar = IntVar(None)
    self.currentEntryVar.set(current)
    self.currentEntry = Entry(parent, textvariable=self.currentEntryVar,width=10)
    self.timeSizeType_value = StringVar()
    self.timeSizeType = Combobox(parent, textvariable=self.timeSizeType_value,state='readonly',width=7)
    self.timeSizeType['values'] = ('sec', 'min', 'hour')
    if timeType=='sec':
      self.timeSizeType.current(0)
    elif timeType=='min':
      self.timeSizeType.current(1)
    elif timeType=='hour':
      self.timeSizeType.current(2)
    self.durationEntryVar = DoubleVar(None)
    self.durationEntryVar.set(duration)
    self.durationEntry = Entry(parent, textvariable=self.durationEntryVar,width=10)
    self.removeLineButton = Button(parent,text="-",width=3, command= lambda:removeLineFunc(rowNumber,[self.voltageEntry,self.currentEntry,self.timeSizeType,self.durationEntry,self.removeLineButton]))

  def getVoltage(self):
    return self.voltageEntryVar.get()

  def getCurrent(self):
    return self.currentEntryVar.get()

  def getTimeType(self):
    return self.timeSizeType_value.get()

  def getDuration(self):
    return self.durationEntryVar.get()

if __name__ == "__main__":
  gui = Gui()
  gui.show()