import queue
import threading
import logging
from datetime import datetime
from apscheduler.scheduler import Scheduler

connectedString = "Connected !"
connectingSting = "Connecting ..."
noDeviceFoundstr= "No device found"
connectString = "CONNECT"
realCurrentString = "REALCURRENT"
realVoltageString = "REALVOLTAGE"
targetCurrentString = "TARGETCURRENT"
targetVoltageString = "TARGETVOLTAGE"
outputOnOffString = "OUTPUTONOFF"


class ThreadHelper():
  def __init__(self, controller):
    self.controller = controller
    self.queue = queue.Queue()

  def __connectWorker__(self, usbPortNumber):
    self.queue.put(connectString)
    self.queue.put(connectingSting)
    connectionSuccessful = self.controller.connect(usbPortNumber)
    self.queue.put(connectString)
    if connectionSuccessful:
      self.queue.put(connectedString)
      if self.__connectWorkerPostFunc__:
        self.__connectWorkerPostFunc__()
    else:
      print("Connect worker: Connection exception. Failed to connect")
      self.queue.put(noDeviceFoundstr)

  def __setTargetVoltageWorker__(self, targetVoltage):
    try:
      self.controller.setTargetVoltage(targetVoltage)
    except Exception as e:
      self.__connectionLost__("set target voltage worker")

  def __setTargetCurrentWorker__(self, targetCurrent):
    try:
      self.controller.setTargetCurrent(targetCurrent)
    except Exception as e:
      self.__connectionLost__("set target current worker")

  def __updateRealCurrentWorker__(self):
    try:
      realCurrent = self.controller.getRealCurrent()
      self.queue.put(realCurrentString)
      self.queue.put(realCurrent)
    except Exception as e:
      self.__connectionLost__("update real current worker")

  def __updateRealVoltageWorker__(self):
    try:
      realVoltage = self.controller.getRealVoltage()
      self.queue.put(realVoltageString)
      self.queue.put(realVoltage)
    except Exception as e:
      self.__connectionLost__("update real voltage worker")

  def __updateTargetCurrentWorker__(self):
    try:
      targetCurrent = self.controller.getTargetCurrent()
      self.queue.put(targetCurrentString)
      self.queue.put(targetCurrent)
    except Exception as e:
      self.__connectionLost__("update target current worker")

  def __updateTargetVoltageWorker__(self):
    try:
      targetVoltage = self.controller.getTargetVoltage()
      self.queue.put(targetVoltageString)
      self.queue.put(targetVoltage)
    except Exception as e:
      self.__connectionLost__("update target voltage worker")

  #TODO
  def __updateOutputOnOffWorker__(self):
    try:
      shouldBeOn = self.controller.getOutputOnOff()
      self.queue.put(outputOnOffString)
      self.queue.put(shouldBeOn)
    except Exception as e:
      self.__connectionLost__("update output on off worker")

  def __connectionLost__(self, source):
    logging.debug("Lost connection in %s", source)
    self.queue.put(connectString)
    self.queue.put(noDeviceFoundstr)
    print("connection lost worker")

  def connect(self, usbPortNumber,  postProcessingFunction = None):
    self.__connectWorkerPostFunc__ = postProcessingFunction
    threading.Thread(target=self.__connectWorker__, args = [usbPortNumber]).start()

  def ledSwitch(self):
    threading.Thread(target=self.__ledSwitchWorker__).start()

  def setTargetVoltage(self, voltage):
    threading.Thread(target=self.__setTargetVoltageWorker__, args = [voltage]).start()

  def setTargetCurrent(self, current):
    threading.Thread(target=self.__setTargetCurrentWorker__, args = [current]).start()

  def updateCurrentAndVoltage(self):
    threading.Thread(target=self.__updateRealCurrentWorker__).start()
    threading.Thread(target=self.__updateRealVoltageWorker__).start()
    threading.Thread(target=self.__updateTargetCurrentWorker__).start()
    threading.Thread(target=self.__updateTargetVoltageWorker__).start()
    threading.Thread(target=self.__updateOutputOnOffWorker__).start()

  def startScheduledJob(self, startingVoltage, startingCurrent, changeType, plusMinus, stepSize, timeStepSize, timeType):
    self.startingVoltage = startingVoltage
    self.startingCurrent = startingCurrent
    self.changeType = changeType
    self.timeType = timeType

    if plusMinus == "+":
      self.valueStep = stepSize
    elif plusMinus == "-":
      self.valueStep = -stepSize

    # Offsets the first increment done by the job
    if self.changeType == "voltage":
      self.scTargetVoltage = startingVoltage - self.valueStep
      self.scTargetCurrent = startingCurrent
    elif self.changeType == "current":
      self.scTargetVoltage = startingVoltage
      self.scTargetCurrent = startingCurrent - self.valueStep

    #Initial run
    self.__scheduleJob__()

    self.sched = Scheduler()
    self.sched.start()

    if timeType == "sec":
      self.sched.add_interval_job(self.__scheduleJob__, seconds=timeStepSize)
    elif timeType == "min":
      self.sched.add_interval_job(self.__scheduleJob__, minutes=timeStepSize)
    elif timeType == "hour":
      self.sched.add_interval_job(self.__scheduleJob__, hours=timeStepSize)

  def stopSceduledJob(self):
    self.sched.shutdown()

  def __scheduleJob__(self):
    if self.changeType == "voltage":
      self.scTargetVoltage += self.valueStep
      self.__setTargetVoltageWorker__(self.scTargetVoltage)
    elif self.changeType == "current":
      self.scTargetCurrent += self.valueStep
      self.__setTargetCurrentWorker__(self.scTargetCurrent)

