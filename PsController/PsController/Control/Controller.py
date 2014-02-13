import logging
import queue
import uuid
from datetime import datetime, timedelta
from DAL.DataAccess import DataAccess
from Utilities.ThreadHelper import ThreadHelper

connectedString = "Connected !"
connectingString = "Connecting ..."
noDeviceFoundstr= "No device found"
connectUpdate = "CONNECT"
realCurrentUpdate = "REALCURRENT"
realVoltageUpdate = "REALVOLTAGE"
preRegVoltageUpdate = "PREREGVOLTAGE"
targetCurrentUpdate = "TARGETCURRENT"
targetVoltageUpdate = "TARGETVOLTAGE"
inputVoltageUpdate = "INPUTVOLTAGE"
outputOnOffUpdate = "OUTPUTONOFF"
scheduleDoneUpdate = "SCHEDULEDONE"
scheduleNewLineUpdate = "SCHEDULENEWLINE"

class Controller():
    def __init__(self, shouldLog = False, loglevel = logging.ERROR):
        if shouldLog:
            logging.basicConfig(format='%(asctime)s %(message)s', filename='PS200.log', level=loglevel)
        
        self.DataAccess = DataAccess()
        self.queue = queue.Queue()
        self.cancelNextGet = queue.Queue()
        self.threadHelper = ThreadHelper()
        self.updateFunctions = {}
        self.connected = False
      
    def connect(self, usbPortNumber, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._connectWorker, [usbPortNumber])
        else:
            return self.DataAccess.connect(usbPortNumber)
    
    def disconnect(self):
        self.DataAccess.disconnect()
    
    def getAvailableUsbPorts(self):
        return self.DataAccess.getAvailableUsbPorts()
   
    def getDeviceUsbPort(self, availableUsbPorts):
      return self.DataAccess.detectDevicePort()
    
    def getAllValues(self):
        return self.DataAccess.getAllValues()
        
    def setTargetVoltage(self, targetVoltage, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._setTargetVoltageWorker, args=[targetVoltage])
        else:
            self.DataAccess.setTargetVoltage(targetVoltage)
   
    def setTargetCurrent(self, targetCurrent, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._setTargetCurrentWorker, args=[targetCurrent])
        else:
            self.DataAccess.setTargetCurrent(targetCurrent)
        
    def setOutputOnOff(self, shouldBeOn, threaded=False):
        if threaded:
            if self.cancelNextGet.qsize() == 0:
                self.cancelNextGet.put("Cancel")
            self.threadHelper.runThreadedJob(self._setOutputOnOffWorker, args=[shouldBeOn])
        else:
            self.DataAccess.setOutputOnOff(shouldBeOn)
   
    def setLogging(self, shouldLog, loglevel):
        if shouldLog:
            logging.basicConfig(level=loglevel)
        else:
            logging.propagate = False
   
    def registerUpdateFunction(self, func, condition):
        if condition not in self.updateFunctions:
            self.updateFunctions[condition] = (None,[]) #(Value, list_of_update_functions)
        self.updateFunctions[condition][1].append(func)

    """
    A call to this function lets the controller know that the UI is ready to receive updates
    """
    def uiPulse(self):
        while self.queue.qsize():
            updateCondition = self.queue.get(0)
            updatedValue = self.queue.get(0)
            value, updateFunctions = self.updateFunctions[updateCondition]
            if value != updatedValue:
                for func in updateFunctions:
                    func(updatedValue)

    def startAutoUpdate(self, interval):
        self.threadHelper.runIntervalJob(self._updateValuesWorker, interval)
      
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
            listOfFunctions.append(self._addJobForLine)
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
        listOfFunctions.append(self._resetDevice)
        listOfFiringTimes.append(nextFireTime)
        listOfArgs.append([startingTargetVoltage, startingTargetCurrent, startingOutputOn])
        self.threadHelper.runSchedule(listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval, loggingTimeInterval,filePath, self._logValuesToFile)
        return True
   
    def stopSchedule(self):
        self.queue.put(scheduleDoneUpdate)
        self.queue.put(uuid.uuid4()) # Add a random UUID to fake a change event
        self.threadHelper.stopSchedule()

    def _updateValuesWorker(self):
        try:
            if self.cancelNextGet.qsize() != 0:
                self.cancelNextGet.get()
                return
            allValues = self.getAllValues()
            if len(allValues) < 7:
                return     
            self.queue.put(realVoltageUpdate)
            self.queue.put(allValues[0])      
            self.queue.put(realCurrentUpdate)
            self.queue.put(allValues[1])      
            self.queue.put(targetVoltageUpdate)
            self.queue.put(allValues[2])     
            self.queue.put(targetCurrentUpdate)
            self.queue.put(allValues[3])     
            self.queue.put(preRegVoltageUpdate)
            self.queue.put(allValues[4])    
            self.queue.put(inputVoltageUpdate)
            self.queue.put(allValues[5]) 
            self.queue.put(outputOnOffUpdate)
            self.queue.put(allValues[6])
        except Exception as e:
            self._connectionLost("_updateValuesWorker")      
        
    def _connectWorker(self, usbPortNumber):
        self.queue.put(connectUpdate)
        self.queue.put(connectingString)
        self.connected = self.connect(usbPortNumber)
        self.queue.put(connectUpdate)
        if self.connected:
            self.queue.put(connectedString)
        else:
            print("Connect worker: Connection exception. Failed to connect")
            self.queue.put(noDeviceFoundstr)
        
    def _setTargetVoltageWorker(self, targetVoltage):
        try:
            self.setTargetVoltage(targetVoltage)
        except Exception as e:
            self._connectionLost("set target voltage worker")
   
    def _setTargetCurrentWorker(self, targetCurrent):
        try:
            self.setTargetCurrent(targetCurrent)
        except Exception as e:
            self._connectionLost("set target current worker")
        
    def _setOutputOnOffWorker(self, shouldBeOn):
        try:
            self.setOutputOnOff(shouldBeOn)
        except Exception as e:
            self._connectionLost("set output on/off worker")    
        
    def _connectionLost(self, source):
        logging.debug("Lost connection in %s", source)
        self.queue.put(connectString)
        self.queue.put(noDeviceFoundstr)
        print("connection lost worker. Connection lost in ", source)
   
    def _addJobForLine(self, line, logToDataFile, filePath):
        self.queue.put(scheduleNewLineString)
        self.queue.put(line.rowNumber)
        self._setTargetVoltageWorker(line.getVoltage())
        self._setTargetCurrentWorker(line.getCurrent())
            
        if logToDataFile:
            self._logValuesToFile(filePath)
   
    def _resetDevice(self, startingTargetVoltage, startingTargetCurrent, startingOutputOn):
        self._setTargetVoltageWorker(startingTargetVoltage)
        self._setTargetCurrentWorker(startingTargetCurrent)
        self.setOutputOnOff(startingOutputOn)
        self.stopSchedule()
   
    def _startTimeIntervalLogging(self, loggingTimeInterval, filePath):
        time.sleep(1) # Sleep for one sec to account for the 1 sec time delay in jobs
        self.threadHelper.runIntervalJob(function = self._logValuesToFile, interval=loggingTimeInterval, args=[filePath])
        
    def _logValuesToFile(self,filePath):
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
    
    
      