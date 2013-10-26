import queue
import threading
import logging
from datetime import datetime, timedelta
from apscheduler.scheduler import Scheduler
import time

connectedString = "Connected !"
connectingSting = "Connecting ..."
noDeviceFoundstr= "No device found"
connectString = "CONNECT"
realCurrentString = "REALCURRENT"
realVoltageString = "REALVOLTAGE"
preRegVoltageString = "PREREGVOLTAGE"
targetCurrentString = "TARGETCURRENT"
targetVoltageString = "TARGETVOLTAGE"
outputOnOffString = "OUTPUTONOFF"
scheduleDoneString = "SCHEDULEDONE"
scheduleNewLineString = "SCHEDULENEWLINE"

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
      self.queue.put(usbPortNumber)
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

  def __updatePreRegVoltageWorker__(self):
    try:
      preRegVoltage = self.controller.getPreRegulatorVoltage()
      self.queue.put(preRegVoltageString)
      self.queue.put(preRegVoltage)
    except Exception as e:
      self.__connectionLost__("update real voltage worker")

  def __updateTargetVoltageWorker__(self):
    try:
      targetVoltage = self.controller.getTargetVoltage()
      self.queue.put(targetVoltageString)
      self.queue.put(targetVoltage)
    except Exception as e:
      self.__connectionLost__("update target voltage worker")

  def __updateOutputOnOffWorker__(self):
    try:
      shouldBeOn = self.controller.getOutputOnOff()
      self.queue.put(outputOnOffString)
      self.queue.put(shouldBeOn)
    except Exception as e:
      self.__connectionLost__("update output on off worker")
      
  def __updateAllValuesWorker__(self):
    try:
      allValues = self.controller.getAllValues()
      listOfValues = allValues.split(";")      
      self.queue.put(realVoltageString)
      self.queue.put(listOfValues[0])      
      self.queue.put(realCurrentString)
      self.queue.put(listOfValues[1])      
      self.queue.put(targetVoltageString)
      self.queue.put(listOfValues[2])     
      self.queue.put(targetCurrentString)
      self.queue.put(listOfValues[3])     
      self.queue.put(preRegVoltageString)
      self.queue.put(listOfValues[4])    
      self.queue.put(outputOnOffString)
      self.queue.put(listOfValues[5])
    except Exception as e:
      self.__connectionLost__("update output on off worker")    

  def __connectionLost__(self, source):
    logging.debug("Lost connection in %s", source)
    self.queue.put(connectString)
    self.queue.put(noDeviceFoundstr)
    print("connection lost worker. Connection lost in ", source)

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
    #threading.Thread(target=self.__updateRealCurrentWorker__).start()
    #threading.Thread(target=self.__updateRealVoltageWorker__).start()
    #threading.Thread(target=self.__updateTargetCurrentWorker__).start()
    #threading.Thread(target=self.__updateTargetVoltageWorker__).start()
    #threading.Thread(target=self.__updatePreRegVoltageWorker__).start()
    #threading.Thread(target=self.__updateOutputOnOffWorker__).start()
    threading.Thread(target=self.__updateAllValuesWorker__).start()
    

  def startSchedule(self,lines,
                    startingTargetVoltage,
                    startingTargetCurrent, 
                    startingOutputOn,
                    logWhenValuesChange=False,
                    filePath=None,
                    useLoggingTimeInterval=False,
                    loggingTimeInterval=0):
    self.sched = Scheduler()
    self.sched.start()

    legalLines = []
    for line in lines:
      if line.getDuration() != 0:
        legalLines.append(line)
    numLines = len(legalLines)
    if numLines == 0:
      return
    nextFireTime = datetime.now() + timedelta(seconds=1)
    for line in lines:
      self.sched.add_date_job(func = self.addJobForLine, date=nextFireTime, args=[line, logWhenValuesChange, filePath])
      timeType = line.getTimeType()
      if timeType == "sec":
        nextFireTime += timedelta(seconds=line.getDuration())
      elif timeType == "min":
        nextFireTime += timedelta(minutes=line.getDuration())
      elif timeType == "hour":
        nextFireTime += timedelta(hours=line.getDuration())
    self.controller.setOutputOnOff(True)
    self.sched.add_date_job(func = self.resetDevice, date=nextFireTime, args=[startingTargetVoltage, startingTargetCurrent, startingOutputOn])
    
    if useLoggingTimeInterval:
      self.startTimeIntervalLogging(loggingTimeInterval,filePath)
    
    return True

  def addJobForLine(self, line, logToDataFile, filePath):
    self.queue.put(scheduleNewLineString)
    self.queue.put(line.rowNumber)
    self.__setTargetVoltageWorker__(line.getVoltage())
    #time.sleep(50 / 1000)
    self.__setTargetCurrentWorker__(line.getCurrent())
        
    if logToDataFile:
      time.sleep(100 / 1000)
      self.logValuesToFile(filePath)

  def resetDevice(self, startingTargetVoltage, startingTargetCurrent, startingOutputOn):
    self.__setTargetVoltageWorker__(startingTargetVoltage)
    #time.sleep(50 / 1000)
    self.__setTargetCurrentWorker__(startingTargetCurrent)
    #time.sleep(50 / 1000)
    self.controller.setOutputOnOff(startingOutputOn)
    self.stopSchedule()

  def stopSchedule(self):
    self.queue.put(scheduleDoneString) # Notify the UI
    self.sched.shutdown()
    try:
      self.intervalLoggingSched.shutdown()
    except:
      pass
      
  def startTimeIntervalLogging(self, loggingTimeInterval, filePath):
    time.sleep(1) # Sleep for one sec to account for the 1 sec time delay in jobs
    self.intervalLoggingSched = Scheduler()
    self.intervalLoggingSched.start()
    self.intervalLoggingSched.add_interval_job(self.logValuesToFile, seconds=loggingTimeInterval, args=[filePath])
    
    
  def logValuesToFile(self,filePath):
    allValues = self.controller.getAllValues()
    listOfValues = allValues.split(";")      
    realVoltage = listOfValues[0]
    realCurrent = listOfValues[1]
    
    #time.sleep(50 / 1000)
    #realVoltage = self.controller.getRealVoltage()
    #time.sleep(50 / 1000)
    #realCurrent = self.controller.getRealCurrent()
    with open(filePath, "a") as myfile:
        fileString = str(datetime.now()) 
        fileString += "\t"  
        fileString += realVoltage
        fileString += "\t"  
        fileString += realCurrent
        fileString += "\n"
        myfile.write(fileString)
