import tkinter
import Arduino
import queue
import threading
import logging

guiRefreshRate = 100
valuesRefreshRate = 3000
connectingString ="Connecting ... "
connectedString = "Connected !    "
noDeviceFoundstr= "No device found"
connectString = "CONNECT"
realCurrentString = "REALCURRENT"
realVoltageString = "REALVOLTAGE"
targetCurrentString = "TARGETCURRENT"
targetVoltageString = "TARGETVOLTAGE"
#mainWindowSize = '500x300+200+200'
mainWindowTitle = "Arduino Controller"

class ThreadHelper():
  def __init__(self, controller, queue):
    self.controller = controller
    self.queue = queue

  def __connectWorker__(self):
    connectionSuccessful = self.controller.connect()
    self.queue.put(connectString)
    if connectionSuccessful:
      self.queue.put(connectedString)
      if self.__connectWorkerPostFunc__:
        self.__connectWorkerPostFunc__()
    else:
      self.queue.put(noDeviceFoundstr)

  def __ledSwitchWorker__(self):
    self.controller.ledSwitch()

  def __setTargetVoltageWorker__(self, targetVoltage):
    self.controller.setTargetVoltage(targetVoltage)

  def __setTargetCurrentWorker__(self, targetCurrent):
    self.controller.setTargetCurrent(targetCurrent)

  def __updateRealCurrentWorker__(self):
    realCurrent = self.controller.getRealCurrent()
    self.queue.put(realCurrentString)
    self.queue.put(realCurrent)

  def __updateRealVoltageWorker__(self):
    realVoltage = self.controller.getRealVoltage()
    self.queue.put(realVoltageString)
    self.queue.put(realVoltage)

  def __updateTargetCurrentWorker__(self):
    targetCurrent = self.controller.getTargetCurrent()
    self.queue.put(targetCurrentString)
    self.queue.put(targetCurrent)

  def __updateTargetVoltageWorker__(self):
    targetVoltage = self.controller.getTargetVoltage()
    self.queue.put(targetVoltageString)
    self.queue.put(targetVoltage)

  def connect(self, postProcessingFunction = None):
    self.__connectWorkerPostFunc__ = postProcessingFunction
    threading.Thread(target=self.__connectWorker__).start()

  def ledSwitch(self):
    threading.Thread(target=self.__ledSwitchWorker__).start()

  def setTargetVoltage(self, voltage):
    threading.Thread(target=self.__setTargetVoltageWorker__, args = voltage).start()

  def setTargetCurrent(self, current):
    threading.Thread(target=self.__setTargetCurrentWorker__, args = current).start()

  def updateCurrentAndVoltage(self):
    threading.Thread(target=self.__updateRealCurrentWorker__).start()
    threading.Thread(target=self.__updateRealVoltageWorker__).start()
    threading.Thread(target=self.__updateTargetCurrentWorker__).start()
    threading.Thread(target=self.__updateTargetVoltageWorker__).start()

class Gui():
  def __init__(self):
    shouldLog = True
    self.queue = queue.Queue()
    self.controller = Arduino.ArduinoController(shouldLog = shouldLog)
    self.threadHelper = ThreadHelper(controller=self.controller, queue=self.queue)
    self.autoRefreshOn = 0
    self.mainWindow = tkinter.Tk()
    self.mainWindow.title(mainWindowTitle)
    self.mainWindow.geometry()
    self.lblStatus = tkinter.Label(self.mainWindow, text="Status: ").grid(row=0, column=0, sticky=tkinter.W)
    self.lblStatusValueVar = tkinter.StringVar(value=connectingString)
    self.lblStatusValue = tkinter.Label(self.mainWindow, textvariable=self.lblStatusValueVar).grid(row=0, column=1, sticky=tkinter.W)
    self.lblEmpty = tkinter.Label(self.mainWindow, text="").grid(row=1, column=0)
    self.valueFrames = ValueFrames(self.mainWindow, setTargetVoltageM=self.threadHelper.setTargetVoltage, setTargetCurrentM=self.threadHelper.setTargetCurrent)
    self.valueFrames.grid(row=2, column=1, columnspan=4)
    self.autoRefreshVar = tkinter.IntVar()
    self.chkAutoRefresh = tkinter.Checkbutton(self.mainWindow, text = "Auto refresh", variable = self.autoRefreshVar, command = lambda: self.autoRefreshClick(self.autoRefreshVar.get()), state=tkinter.DISABLED)
    self.chkAutoRefresh.grid(row=3, column = 3, sticky=tkinter.E)
    self.btnRefresh = tkinter.Button(self.mainWindow, text = "Refresh",command = self.refreshClick, state=tkinter.DISABLED, pady=5)
    self.btnRefresh.grid(row=3, column = 4, sticky=tkinter.E)
    self.ledSwitchButton = tkinter.Button(self.mainWindow, text = "Led button", width = 20, command = self.ledClick)
    self.ledSwitchButton.grid(row=4, column=2)
    self.chkloggingVar = tkinter.IntVar(value=1)
    self.chklogging = tkinter.Checkbutton(self.mainWindow, text = "Log", variable = self.chkloggingVar, command = self.loggingClick)
    self.chklogging.grid(row=5, column=2)

  def refreshClick(self):
    self.threadHelper.updateCurrentAndVoltage()

  def loggingClick(self):
    checkedValue = self.chkloggingVar.get()
    self.controller.setLogging(checkedValue)

  def autoRefreshClick(self, autoRefreshValue):
    logging("Autorefresh clicked. Value of auto refresh: ", autoRefreshValue)
    self.autoRefreshOn = autoRefreshValue
    if autoRefreshValue:
      self.periodicCurrentVoltageUpdate()

  def ledClick(self):
    self.threadHelper.ledSwitch()

  def connect(self):
    self.periodicUiUpdate()
    self.autoRefreshOn = self.autoRefreshVar.get()
    self.threadHelper.connect(self.onConnect)

  def onConnect(self):
    self.threadHelper.updateCurrentAndVoltage()
    if self.autoRefreshOn:
      self.periodicCurrentVoltageUpdate()

  def connectedStateChanged(self, connected):
    chkAutoRefresh = self.chkAutoRefresh
    btnRefresh = self.btnRefresh
    btnSetTargetVoltage = self.valueFrames.targetValues.btnSetTargetVoltage
    btnSetTargetCurrent = self.valueFrames.targetValues.btnSetTargetCurrent

    if connected:
      newState = tkinter.NORMAL
    else:
      newState = tkinter.DISABLED
    chkAutoRefresh["state"] = newState
    btnRefresh["state"] = newState
    btnSetTargetVoltage["state"] = newState
    btnSetTargetCurrent["state"] = newState

  def periodicUiUpdate(self):
    if self.queue.qsize():
      try:
        action = self.queue.get(0)
        if action == connectString:
          connectStatus = self.queue.get(0)
          self.lblStatusValueVar.set(connectStatus)

          if connectStatus == connectedString:
            self.connectedStateChanged(True)
          else:
            self.connectedStateChanged(False)

        elif action == realCurrentString:
          realCurrentValue = self.queue.get(0)
          self.valueFrames.realValues.currentEntryVar.set(realCurrentValue)
        elif action == realVoltageString:
          newVoltageValue = self.queue.get(0)
          self.valueFrames.realValues.voltageEntryVar.set(newVoltageValue)
        elif action == targetCurrentString:
          targetCurrentValue = self.queue.get(0)
          self.valueFrames.targetValues.currentEntryVar.set(targetCurrentValue)
        elif action == targetVoltageString:
          targetVoltageValue = self.queue.get(0)
          self.valueFrames.targetValues.voltageEntryVar.set(targetVoltageValue)
      except queue.Empty:
        pass
      finally:
        self.mainWindow.after(guiRefreshRate, self.periodicUiUpdate)
    else:
      self.mainWindow.after(guiRefreshRate, self.periodicUiUpdate)

  def periodicCurrentVoltageUpdate(self):
    if self.autoRefreshOn:
      self.threadHelper.updateCurrentAndVoltage()
      self.mainWindow.after(valuesRefreshRate, self.periodicCurrentVoltageUpdate)

  def show(self):
    self.connect()
    self.mainWindow.mainloop()

class ValueFrame(tkinter.Frame):
  def __init__(self, parent, frameType, setTargetVoltageM, setTargetCurrentM):
    tkinter.Frame.__init__(self,parent)
    self.parent = parent
    self.setTargetVoltageM = setTargetVoltageM
    self.setTargetCurrentM = setTargetCurrentM

    headerText = ""
    entryState = ""
    if frameType == "real":
      headerText = "Measured values"
      entryState = "disabled"
    elif frameType == 'target':
      headerText = "Target values"
      entryState = "normal"
    lblheader = tkinter.Label(self, text=headerText).pack()
    innerFrame = tkinter.Frame(self)
    innerFrame.pack(fill=tkinter.BOTH,expand=1, ipady=1, padx=10, pady=5)
    voltageLabel = tkinter.Label(innerFrame, text="Voltage").grid(row=0,column=0)
    self.voltageEntryVar = tkinter.IntVar(None)
    self.voltageEntry = tkinter.Entry(innerFrame, textvariable=self.voltageEntryVar, state=entryState)
    self.voltageEntry.grid(row=0, column=1)
    currentLabel = tkinter.Label(innerFrame, text="Current").grid(row=1,column=0)
    self.currentEntryVar = tkinter.IntVar(None)
    self.currentEntry = tkinter.Entry(innerFrame, textvariable=self.currentEntryVar, state=entryState)
    self.currentEntry.grid(row=1, column=1)

    if frameType == 'target':
      self.btnSetTargetCurrent = tkinter.Button(innerFrame, text = "Set",command = lambda: self.setTargetCurrent(self.currentEntry.get()), state=tkinter.DISABLED)
      self.btnSetTargetCurrent.grid(row=1, column = 2, sticky=tkinter.E)
      self.btnSetTargetVoltage = tkinter.Button(innerFrame, text = "Set", command = lambda: self.setTargetVoltage(self.voltageEntry.get()), state=tkinter.DISABLED)
      self.btnSetTargetVoltage.grid(row=0, column = 2, sticky=tkinter.E)

  def setTargetVoltage(self, targetVoltage):
    self.setTargetVoltageM(targetVoltage)

  def setTargetCurrent(self, targetCurrent):
    self.setTargetCurrentM(targetCurrent)

class ValueFrames(tkinter.Frame):
  def __init__(self, parent, setTargetVoltageM, setTargetCurrentM):
    tkinter.Frame.__init__(self,parent, borderwidth=1, relief=tkinter.RAISED)
    self.parent = parent
    self.realValues = ValueFrame(self,frameType="real", setTargetVoltageM=setTargetVoltageM, setTargetCurrentM=setTargetCurrentM)
    self.realValues.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)
    separator=tkinter.Frame(self,width=3, relief=tkinter.SUNKEN, bd=1)
    separator.pack(fill=tkinter.Y,side=tkinter.LEFT, pady=5)
    self.targetValues = ValueFrame(self,frameType="target", setTargetVoltageM=setTargetVoltageM, setTargetCurrentM=setTargetCurrentM)
    self.targetValues.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)


if __name__ == "__main__":
  gui = Gui()
  gui.show()