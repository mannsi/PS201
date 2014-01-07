from DataLayer import DataLayer
import ThreadHelper
import logging
import queue
import threading
from datetime import datetime, timedelta

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

class Controller():
    def __init__(self, shouldLog = False, loglevel = logging.ERROR):
        if shouldLog:
            logging.basicConfig(format='%(asctime)s %(message)s', filename='PS200.log', level=loglevel)
        
        self.dataLayer = DataLayer()
        self.queue = queue.Queue()
        self.cancelNextGet = queue.Queue()
        self.threadHelper = ThreadHelper.ThreadHelper()
      
    def connect(self, usbPortNumber, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.__connectWorker__, [usbPortNumber])
        else:
            return self.dataLayer.connect(usbPortNumber)
    
    def disconnect(self):
        self.dataLayer.disconnect()
    
    def getAvailableUsbPorts(self):
        return self.dataLayer.getAvailableUsbPorts()
   
    def getDeviceUsbPort(self, availableUsbPorts):
      return self.dataLayer.detectDevicePort()
    
    def getAllValues(self):
        return self.dataLayer.getAllValues()
        
    def setTargetVoltage(self, targetVoltage, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.__setTargetVoltageWorker__, args=[targetVoltage])
        else:
            self.dataLayer.setTargetVoltage(targetVoltage)
   
    def setTargetCurrent(self, targetCurrent, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.__setTargetCurrentWorker__, args=[targetCurrent])
        else:
            self.dataLayer.setTargetCurrent(targetCurrent)
        
    def setOutputOnOff(self, shouldBeOn, threaded=False):
        if threaded:
            if self.cancelNextGet.qsize() == 0:
                self.cancelNextGet.put("Cancel")
            self.threadHelper.runThreadedJob(self.__setOutputOnOffWorker__, args=[shouldBeOn])
        else:
            self.dataLayer.setOutputOnOff(shouldBeOn)
   
    def setLogging(self, shouldLog, loglevel):
        if shouldLog:
            logging.basicConfig(level=loglevel)
        else:
            logging.propagate = False
   
    def startAutoUpdate(self, interval):
        self.threadHelper.runIntervalJob(self.__updateValuesWorker__, interval)
      
    def __updateValuesWorker__(self):
        try:
            if self.cancelNextGet.qsize() != 0:
                self.cancelNextGet.get()
                return
            allValues = self.getAllValues()
            if len(allValues) < 6:
                return     
            self.queue.put(realVoltageString)
            self.queue.put(allValues[0])      
            self.queue.put(realCurrentString)
            self.queue.put(allValues[1])      
            self.queue.put(targetVoltageString)
            self.queue.put(allValues[2])     
            self.queue.put(targetCurrentString)
            self.queue.put(allValues[3])     
            self.queue.put(preRegVoltageString)
            self.queue.put(allValues[4])    
            self.queue.put(outputOnOffString)
            self.queue.put(allValues[5])
        except Exception as e:
            self.__connectionLost__("__updateValuesWorker__")      
        
    def __connectWorker__(self, usbPortNumber):
        self.queue.put(connectString)
        self.queue.put(connectingSting)
        connectionSuccessful = self.connect(usbPortNumber)
        self.queue.put(connectString)
        if connectionSuccessful:
            self.queue.put(connectedString)
            self.queue.put(usbPortNumber)
        else:
            print("Connect worker: Connection exception. Failed to connect")
            self.queue.put(noDeviceFoundstr)
        
    def __setTargetVoltageWorker__(self, targetVoltage):
        try:
            self.setTargetVoltage(targetVoltage)
        except Exception as e:
            self.__connectionLost__("set target voltage worker")
   
    def __setTargetCurrentWorker__(self, targetCurrent):
        try:
            self.setTargetCurrent(targetCurrent)
        except Exception as e:
            self.__connectionLost__("set target current worker")
        
    def __setOutputOnOffWorker__(self, shouldBeOn):
        try:
            self.setOutputOnOff(shouldBeOn)
        except Exception as e:
            self.__connectionLost__("set output on/off worker")    
        
    def __connectionLost__(self, source):
        logging.debug("Lost connection in %s", source)
        self.queue.put(connectString)
        self.queue.put(noDeviceFoundstr)
        print("connection lost worker. Connection lost in ", source)
       
    def startSchedule(self,
                      lines,
                      startingTargetVoltage,
                      startingTargetCurrent, 
                      startingOutputOn,
                      logWhenValuesChange=False,
                      filePath=None,
                      useLoggingTimeInterval=False,
                      loggingTimeInterval=0):
    
        listOfFunctions = []
        listOfFiringTimes = []
        listOfArgs = []
        
        legalLines = []
        for line in lines:
            if line.getDuration() != 0:
                legalLines.append(line)
        numLines = len(legalLines)
        if numLines == 0:
            return
        nextFireTime = datetime.now() + timedelta(seconds=1)
        for line in legalLines:
            listOfFunctions.append(self.__addJobForLine__)
            listOfFiringTimes.append(nextFireTime)
            listOfArgs.append([line, logWhenValuesChange, filePath])
            timeType = line.getTimeType()
            if timeType == "sec":
                nextFireTime += timedelta(seconds=line.getDuration())
            elif timeType == "min":
                nextFireTime += timedelta(minutes=line.getDuration())
            elif timeType == "hour":
                nextFireTime += timedelta(hours=line.getDuration())
        self.setOutputOnOff(True)
        listOfFunctions.append(self.__resetDevice__)
        listOfFiringTimes.append(nextFireTime)
        listOfArgs.append([startingTargetVoltage, startingTargetCurrent, startingOutputOn])
        self.threadHelper.runSchedule(listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval, loggingTimeInterval,filePath, self.__logValuesToFile__)
        return True
   
    def stopSchedule(self):
        self.queue.put(scheduleDoneString) # Notify the UI
        self.threadHelper.stopSchedule()
   
    def __addJobForLine__(self, line, logToDataFile, filePath):
        self.queue.put(scheduleNewLineString)
        self.queue.put(line.rowNumber)
        self.__setTargetVoltageWorker__(line.getVoltage())
        self.__setTargetCurrentWorker__(line.getCurrent())
            
        if logToDataFile:
            self.__logValuesToFile__(filePath)
   
    def __resetDevice__(self, startingTargetVoltage, startingTargetCurrent, startingOutputOn):
        self.__setTargetVoltageWorker__(startingTargetVoltage)
        self.__setTargetCurrentWorker__(startingTargetCurrent)
        self.setOutputOnOff(startingOutputOn)
        self.stopSchedule()
   
    def __startTimeIntervalLogging__(self, loggingTimeInterval, filePath):
        time.sleep(1) # Sleep for one sec to account for the 1 sec time delay in jobs
        self.threadHelper.runIntervalJob(function = self.__logValuesToFile__, interval=loggingTimeInterval, args=[filePath])
        
    def __logValuesToFile__(self,filePath):
        allValues = self.getAllValues()
        listOfValues = allValues.split(";")      
        realVoltage = listOfValues[0]
        realCurrent = listOfValues[1]
        with open(filePath, "a") as myfile:
            fileString = str(datetime.now()) 
            fileString += "\t"  
            fileString += str(realVoltage)
            fileString += "\t"  
            fileString += str(realCurrent)
            fileString += "\n"
            myfile.write(fileString)
    
    
      