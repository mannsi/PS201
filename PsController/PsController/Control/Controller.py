import logging
import queue
import uuid
from datetime import datetime, timedelta
from PsController.DAL.DataAccess import DataAccess
from PsController.Utilities.ThreadHelper import ThreadHelper
from PsController.Model.DeviceValues import DeviceValues

_connectUpdate = "CONNECT"
_realCurrentUpdate = "REALCURRENT"
_realVoltageUpdate = "REALVOLTAGE"
_preRegVoltageUpdate = "PREREGVOLTAGE"
_targetCurrentUpdate = "TARGETCURRENT"
_targetVoltageUpdate = "TARGETVOLTAGE"
_inputVoltageUpdate = "INPUTVOLTAGE"
_outputOnOffUpdate = "OUTPUTONOFF"
_scheduleDoneUpdate = "SCHEDULEDONE"
_scheduleNewLineUpdate = "SCHEDULENEWLINE"

class Controller():
    def __init__(self, shouldLog = False, loglevel = logging.ERROR):
        if shouldLog:
            logging.basicConfig(format='%(asctime)s %(message)s', filename='PS200.log', level=loglevel)
        
        self.DataAccess = DataAccess()
        self.queue = queue.Queue()
        self.cancelNextGet = queue.Queue()
        self.threadHelper = ThreadHelper()
        self.updateParameters = {}
        self.connected = False
        self.currentValues = DeviceValues()
        self.registerListeners()
        self.connectedString = "Connected !"
        self.connectingString = "Connecting ..."
        self.noDeviceFoundstr= "No device found"

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
            try:
                self.DataAccess.setTargetVoltage(targetVoltage)
            except Exception as e:
                self.disconnect()
   
    def setTargetCurrent(self, targetCurrent, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._setTargetCurrentWorker, args=[targetCurrent])
        else:
            try:
                self.DataAccess.setTargetCurrent(targetCurrent)
            except Exception as e:
                self.disconnect()
        
    def setOutputOnOff(self, shouldBeOn, threaded=False):
        if threaded:
            if self.cancelNextGet.qsize() == 0:
                self.cancelNextGet.put("Cancel")
            self.threadHelper.runThreadedJob(self._setOutputOnOffWorker, args=[shouldBeOn])
        else:
            try:
                self.DataAccess.setOutputOnOff(shouldBeOn)
            except Exception as e:
                self.disconnect()
   
    def setLogging(self, shouldLog, loglevel):
        if shouldLog:
            logging.basicConfig(level=loglevel)
        else:
            logging.propagate = False
   
    def _registerUpdateFunction(self, func, condition):
        if condition not in self.updateParameters:
            self.updateParameters[condition] = [None,[]] #(Value, list_of_update_functions)
        self.updateParameters[condition][1].append(func)

    def NotifyConnectedUpdate(self, func):
        self._registerUpdateFunction(func, _connectUpdate)

    def NotifyRealCurrentUpdate(self, func):
        self._registerUpdateFunction(func, _realCurrentUpdate)

    def NotifyRealVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _realVoltageUpdate)

    def NotifyPreRegVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _preRegVoltageUpdate)

    def NotifyTargetCurrentUpdate(self, func):
        self._registerUpdateFunction(func, _targetCurrentUpdate)

    def NotifyTargetVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _targetVoltageUpdate)

    def NotifyInputVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _inputVoltageUpdate)

    def NotifyOutputUpdate(self, func):
        self._registerUpdateFunction(func, _outputOnOffUpdate)

    def NotifyScheduleDoneUpdate(self, func):
        self._registerUpdateFunction(func, _scheduleDoneUpdate)

    def NotifyScheduleLineUpdate(self, func):
        self._registerUpdateFunction(func, _scheduleNewLineUpdate)
         
    """
    A call to this function lets the controller know that the UI is ready to receive updates
    """
    def uiPulse(self):
        while self.queue.qsize():
            updateCondition = self.queue.get(0)
            updatedValue = self.queue.get(0)
            value, updateFunctions = self.updateParameters[updateCondition]
            if value != updatedValue:
                self.updateParameters[updateCondition][0] = updatedValue
                for func in updateFunctions:
                    func(updatedValue)

    def startAutoUpdate(self, interval):
        self.autoUpdateScheduler = self.threadHelper.runIntervalJob(self._updateValuesWorker, interval)
    
    def stopAutoUpdate(self):
        if self.autoUpdateScheduler:
            self.autoUpdateScheduler.shutdown()

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
            self.queue.put(_realVoltageUpdate)
            self.queue.put(allValues[0])      
            self.queue.put(_realCurrentUpdate)
            self.queue.put(allValues[1])      
            self.queue.put(_targetVoltageUpdate)
            self.queue.put(allValues[2])     
            self.queue.put(_targetCurrentUpdate)
            self.queue.put(allValues[3])     
            self.queue.put(_preRegVoltageUpdate)
            self.queue.put(allValues[4])    
            self.queue.put(_inputVoltageUpdate)
            self.queue.put(allValues[5]) 
            self.queue.put(_outputOnOffUpdate)
            self.queue.put(allValues[6])
        except Exception as e:
            self._connectionLost("_updateValuesWorker")      
        
    def _connectWorker(self, usbPortNumber):
        self.queue.put(_connectUpdate)
        self.queue.put((0, self.connectingString))
        self.connected = self.connect(usbPortNumber)
        self.queue.put(_connectUpdate)
        if self.connected:
            self.queue.put((1,self.connectedString))
        else:
            print("Connect worker: Connection exception. Failed to connect")
            self.queue.put((0,self.noDeviceFoundstr))
        
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
        self.queue.put(_connectUpdate)
        self.queue.put((0,self.noDeviceFoundstr))
        self.stopAutoUpdate()
        print("connection lost worker. Connection lost in ", source)
   
    def _addJobForLine(self, line, logToDataFile, filePath):
        self.queue.put(scheduleNewLineUpdate)
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

    def registerListeners(self):
        self.NotifyRealCurrentUpdate(self.realCurrentUpdate)
        self.NotifyRealVoltageUpdate(self.realVoltageUpdate)
        self.NotifyTargetCurrentUpdate(self.targetCurrentUpdate)
        self.NotifyTargetVoltageUpdate(self.targetVoltageUpdate)
        self.NotifyInputVoltageUpdate(self.inputVoltageUpdate)
        self.NotifyOutputUpdate(self.outPutOnOffUpdate)
        self.NotifyPreRegVoltageUpdate(self.preRegVoltageUpdate)

    def targetVoltageUpdate(self, newTargetVoltage):
        self.currentValues.targetVoltage = float(newTargetVoltage)

    def inputVoltageUpdate(self, newInputVoltage):
        self.currentValues.inputVoltage = float(newInputVoltage)
    
    def targetCurrentUpdate(self, newTargetCurrent):
        self.currentValues.targetCurrent = int(newTargetCurrent)
    
    def realVoltageUpdate(self, newRealVoltage):
        self.currentValues.realVoltage = newRealVoltage
    
    def realCurrentUpdate(self, newRealCurrent):
        self.currentValues.realCurrent = newRealCurrent
    
    def outPutOnOffUpdate(self, newOutputOn):
        self.currentValues.outputOn = newOutputOn
    
    def preRegVoltageUpdate(self, preRegVoltage):
        self.currentValues.preRegVoltage = preRegVoltage
    
    
    
      