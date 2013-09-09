# TODO
# Finish getOnOff function in controller
# Add Program tab

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
mainWindowSize = '600x300'
mainWindowTitle = "PSP200 Controller"

normalWidgetList = []
inverseWidgetList = []
controller = PspController.Controller(loglevel = logging.DEBUG)

class Gui():
  def __init__(self):
    self.guiRefreshRate = 100
    self.deviceRefreshRate = 2000
    self.threadHelper = ThreadHelper.ThreadHelper(controller)
    self.setAvailableUsbPorts()

  def connectToDevice(self, usbPort):
    self.periodicUiUpdate()
    if usbPort in self.avilableUsbPorts:
      usbPortNumber = self.avilableUsbPorts[usbPort]
    else:
      usbPortNumber = usbPort
    self.threadHelper.connect(usbPortNumber, self.onConnectToDevice)

  def setAvailableUsbPorts(self):
    self.avilableUsbPorts = controller.getAvailableUsbPorts()

  def onConnectToDevice(self):
    self.connected = True
    self.periodicValuesUpdate()

  def targetVoltageUpdate(self, targetVoltage):
    self.topPanel.voltageFrame.voltageEntryVar.set(targetVoltage)

  def targetCurrentUpdate(self, targetCurrent):
    self.topPanel.currntFrame.currentEntryVar.set(targetCurrent)

  def realVoltageUpdate(self, realVoltage):
    self.tabControl.ManualTab.voltageEntryVar.set(realVoltage)

  def realCurrentUpdate(self, realCurrent):
    self.tabControl.ManualTab.currentEntryVar.set(realCurrent)

  def outPutOnOffUpdate(self, shouldBeOn):
    self.topPanel.chkOutputOnVar.set(shouldBeOn)

  """
  Periodically checks the threadHelper queue for updates to the UI.
  """
  def periodicUiUpdate(self):
    if self.threadHelper.queue.qsize():
      try:
        action = self.threadHelper.queue.get(0)
        if action == ThreadHelper.connectString:
          connectStatus = self.threadHelper.queue.get(0)
          self.topPanel.lblStatusValueVar.set(connectStatus)
          if connectStatus == ThreadHelper.connectedString:
            self.connectedStateChanged(True)
          elif connectStatus == noDeviceFoundstr:
            # When this state is reached I must stop listening more for this state since many thread will return this state
            # I also have to stop the current threads until the connectedString is returned
            print("periodic update UI no device found. Queue size ", self.threadHelper.queue.qsize())
            self.connected = False
            self.connectedStateChanged(False)

        elif action == ThreadHelper.realCurrentString:
          realCurrentValue = self.threadHelper.queue.get(0)
          self.realCurrentUpdate(realCurrentValue)
        elif action == ThreadHelper.realVoltageString:
          realVoltageValue = self.threadHelper.queue.get(0)
          self.realVoltageUpdate(realVoltageValue)
        elif action == ThreadHelper.targetCurrentString:
          targetCurrentValue = self.threadHelper.queue.get(0)
          self.targetCurrentUpdate(targetCurrentValue)
        elif action == ThreadHelper.targetVoltageString:
          targetVoltageValue = self.threadHelper.queue.get(0)
          self.targetVoltageUpdate(targetVoltageValue)
        elif action == ThreadHelper.outputOnOffString:
          outputOnOff = self.threadHelper.queue.get(0)
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
        self.threadHelper.updateCurrentAndVoltage()
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
    self.chkOutputOn = Checkbutton(self, text = "Output ON", variable = self.chkOutputOnVar, state = DISABLED, command = self.outPutOnOff)
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
    self.voltageEntryVar = IntVar(None)
    self.voltageEntry = Entry(self, textvariable=self.voltageEntryVar, state=DISABLED)
    self.voltageEntry.pack(side=RIGHT)
    normalWidgetList.append(self.voltageEntry)
    self.voltageLabel = Label(self, text="Output voltage:").pack(side=RIGHT)

class CurrentFrame(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    self.currentEntryVar = IntVar(None)
    self.currentEntry = Entry(self, textvariable=self.currentEntryVar, state=DISABLED)
    self.currentEntry.pack(side=RIGHT)
    normalWidgetList.append(self.currentEntry)
    self.currentLabel = Label(self, text="Output current:").pack(side=RIGHT)

class TabControl(Notebook):
  def __init__(self, parent):
    Notebook.__init__(self, parent, name='tab control 123')
    self.add(ManualTab(self), text='Manual')
    self.add(Frame(), text='Program')
    self.add(Frame(), text='Graph')

class ManualTab(Frame):
  def __init__(self, parent):
    Frame.__init__(self,parent)
    parent.ManualTab = self
    entryState = DISABLED
    innerFrame = Frame(self)
    innerFrame.pack(fill=BOTH,expand=1, ipady=1, padx=10, pady=5)
    voltageLabel = Label(innerFrame, text="Voltage").grid(row=0,column=0)
    self.voltageEntryVar = IntVar(None)
    self.voltageEntry = Entry(innerFrame, textvariable=self.voltageEntryVar, state=entryState)
    self.voltageEntry.grid(row=0, column=1)
    normalWidgetList.append(self.voltageEntry)
    currentLabel = Label(innerFrame, text="Current").grid(row=1,column=0)
    self.currentEntryVar = IntVar(None)
    self.currentEntry = Entry(innerFrame, textvariable=self.currentEntryVar, state=entryState)
    self.currentEntry.grid(row=1, column=1)
    normalWidgetList.append(self.currentEntry)
    self.btnSetTargetCurrent = Button(innerFrame, text = "Set", state=entryState)
    self.btnSetTargetCurrent.grid(row=1, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetCurrent)
    self.btnSetTargetVoltage = Button(innerFrame, text = "Set", state=entryState)
    self.btnSetTargetVoltage.grid(row=0, column = 2, sticky=E)
    normalWidgetList.append(self.btnSetTargetVoltage)

if __name__ == "__main__":
  gui = Gui()
  gui.show()