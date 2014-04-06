import logging
import queue
import uuid
import time
import threading
from datetime import datetime, timedelta
from PsController.DAL.SerialDataAccess import DataAccess
from PsController.Utilities.ThreadHelper import ThreadHelper
from PsController.Model.DeviceValues import DeviceValues
from PsController.Model.Constants import *
from PsController.DAL.SerialConnection import SerialConnection
from PsController.Utilities.Crc import Crc16
from PsController.Utilities.DeviceResponse import DeviceCommunication

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
_defaultUsbPortUpdate = "DEFAULTUSBPORT"

_CONNECTED_STRING = "Connected !"
_CONNECTING_STRING = "Connecting ..."
_NO_DEVICE_FOUND_STRING= "No device found"
_NO_USBPORT_SELECTED_STRING = "No usb port selected"
_LOST_CONNECTION_STRING = "Lost connection"

class Controller():
    def __init__(self):
        self.logger = None
        self.setLogging(logging.ERROR)
        self.connectionLock = threading.Lock()
        self.queue = queue.Queue()
        self.threadHelper = ThreadHelper()
        self.updateParameters = {}
        self.connected = False
        self.currentValues = DeviceValues()
        self.connection = self._createConnection()
        self.connection.notifyOnConnectionLost(self._connectionLost)
        self._registerListeners()

    def connect(self, usbPortNumber, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._connectWorker, [usbPortNumber])
        else:
            try:
                if usbPortNumber == '' or usbPortNumber == None:
                    self.logger.debug("Empty usb port given")
                    return False
                with self.connectionLock:
                    self.connection.connect(usbPortNumber)
                    return self.connection.connected
            except Exception as e:
                self.logger.error("Device not found on given port")
                self.logger.exception(e)
                return False

    def disconnect(self):
        with self.connectionLock:
            self.connection.disconnect()
    
    def setLogging(self, logLevel):
        if not self.logger:
            self.logger = logging.getLogger("PS201Logger")
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fileHandler = logging.FileHandler("PS201.log")      
            fileHandler.setFormatter(formatter)
            self.logger.addHandler(fileHandler)
            printHandler = logging.StreamHandler()
            printHandler.setFormatter(formatter)
            self.logger.addHandler(printHandler)

            # Overwhelming when this is set to debug
            logging.getLogger("apscheduler.scheduler").setLevel(logging.ERROR) 

        self.logger.setLevel(logLevel)

    def getAvailableUsbPorts(self):
        defaultPort = ""
        with self.connectionLock:
            usbPorts = self.connection.availableConnections()
        return usbPorts

    def getDeviceUsbPort(self, allUsbPorts=None, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._getDeviceUsbPortWorker, args=[allUsbPorts])
            return None
        else:
            with self.connectionLock:
                if not allUsbPorts:
                    allUsbPorts = self.connection.availableConnections()
                for port in usbPorts:
                    if self.connection.deviceOnPort(port):
                        return port
                return None

    def setTargetVoltage(self, targetVoltage, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setTargetVoltage, args=[targetVoltage])
        else:
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to set voltage when not connected to device")
                    return
                DataAccess.sendValueToDevice(self.connection, READ_TARGET_VOLTAGE,targetVoltage)
                self._checkDeviceForAcknowledgement(READ_TARGET_VOLTAGE)
   
    def setTargetCurrent(self, targetCurrent, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setTargetCurrent, args=[targetCurrent])
        else:
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to set current when not connected to device")
                    return
                DataAccess.sendValueToDevice(self.connection, READ_TARGET_CURRENT,targetCurrent)
                self._checkDeviceForAcknowledgement(READ_TARGET_CURRENT)
        
    def setOutputOnOff(self, shouldBeOn, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setOutputOnOff, args=[shouldBeOn])
        else:
            setValue = TURN_OFF_OUTPUT
            if shouldBeOn:
                setValue = TURN_ON_OUTPUT
            with self.connectionLock:   
                if not self.connected:
                    self.logger.debug("Trying to set output when not connected to device")
                    return
                DataAccess.sendValueToDevice(self.connection,setValue, shouldBeOn)
                self._checkDeviceForAcknowledgement(setValue)
   
    """
    Runs the func function when connection status is updated through auto update
    """
    def notifyConnectedUpdate(self, func):
        self._registerUpdateFunction(func, _connectUpdate)

    """
    Runs the func function when real current value changes through auto update
    """
    def notifyRealCurrentUpdate(self, func):
        self._registerUpdateFunction(func, _realCurrentUpdate)

    """
    Runs the func function when real voltage value changes through auto update
    """
    def notifyRealVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _realVoltageUpdate)
    
    """
    Runs the func function when pre reg voltage value changes through auto update
    """
    def notifyPreRegVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _preRegVoltageUpdate)

    """
    Runs the func function when target current value changes through auto update
    """
    def notifyTargetCurrentUpdate(self, func):
        self._registerUpdateFunction(func, _targetCurrentUpdate)

    """
    Runs the func function when target voltage value changes through auto update
    """
    def notifyTargetVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _targetVoltageUpdate)

    """
    Runs the func function when input voltage value changes through auto update
    """
    def notifyInputVoltageUpdate(self, func):
        self._registerUpdateFunction(func, _inputVoltageUpdate)

    """
    Runs the func function when output setting changes through auto update
    """
    def notifyOutputUpdate(self, func):
        self._registerUpdateFunction(func, _outputOnOffUpdate)

    """
    Runs the func function when a schedule finishes
    """
    def notifyScheduleDoneUpdate(self, func):
        self._registerUpdateFunction(func, _scheduleDoneUpdate)

    """
    Runs the func function when the currently running schedule line finishes
    """
    def notifyScheduleLineUpdate(self, func):
        self._registerUpdateFunction(func, _scheduleNewLineUpdate)
         
    """
    Runs the func function when the default usb port is updated 
    """
    def notifyDefaultUsbPortUpdate(self, func):
        self._registerUpdateFunction(func, _defaultUsbPortUpdate)
         
    """
    A call to this function lets the controller know that the UI is ready to receive updates
    """
    def uiPulse(self):
        try:
            while self.queue.qsize():
                updateCondition = self.queue.get(0)
                updatedValue = self.queue.get(0)
                value, updateFunctions = self.updateParameters[updateCondition]
                if value != updatedValue:
                    self.updateParameters[updateCondition][0] = updatedValue
                    for func in updateFunctions:
                        func(updatedValue)
        except Exception as e:
            self.logger.exception(e)
            self.queue.queue.clear()

    def startAutoUpdate(self, interval, updateType):
        if updateType == 0:
            # Polling updates
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to start polling auto update when not connected to device")
                    return
                self.connection.clearBuffer()
                DataAccess.sendValueToDevice(self.connection,STOP_STREAM,'')
                self._checkDeviceForAcknowledgement(STOP_STREAM)
            self.autoUpdateScheduler = self.threadHelper.runIntervalJob(self._updateAllValuesWorker, interval)
        elif updateType == 1:
            # Streaming updates
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to start streaming auto update when not connected to device")
                    return
                DataAccess.sendValueToDevice(self.connection,START_STREAM, '')
                self._checkDeviceForAcknowledgement(START_STREAM)
                self.threadHelper.runThreadedJob(self._updateAllValuesWorker, args=[])
            self.autoUpdateScheduler = self.threadHelper.runIntervalJob(self._updateStreamValueWorker, interval)
    
    def stopAutoUpdate(self):
        if self.autoUpdateScheduler:
            try:
                self.autoUpdateScheduler.shutdown(wait = False)
            except Exception as e:
                self.logger.exception(e)

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
        self.queue.put(_scheduleDoneUpdate)
        self.queue.put(uuid.uuid4()) # Add a random UUID to fake a change event
        self.threadHelper.stopSchedule()
        self._resetScheduleLineParameter()

    def _resetScheduleLineParameter(self):
        self.updateParameters[_scheduleNewLineUpdate][0] = -1

    def getAllValues(self):
        try:
            deviceValue = self._getValueFromDevice(WRITE_ALL)
            if not deviceValue: return
            allValues = [float(x) for x in deviceValue.split(";")]
            return allValues
        except Exception as e:     
            self.logger.exception(e)

    def getRealVoltage(self):
        value = self._getValueFromDevice(WRITE_REAL_VOLTAGE)
        if value is None: return None
        return float(value)

    def getRealCurrent(self):
        value = self._getValueFromDevice(WRITE_REAL_CURRENT)
        if value is None: return None
        return float(value)
    
    def getPreRegulatorVoltage(self):
        value = self._getValueFromDevice(WRITE_PREREGULATOR_VOLTAGE)
        if value is None: return None
        return float(value)
    
    def getTargetVoltage(self):
        value = self._getValueFromDevice(WRITE_TARGET_VOLTAGE)
        if value is None: return None
        return float(value)
    
    def getTargetCurrent(self):
        value = self._getValueFromDevice(WRITE_TARGET_CURRENT)
        if value is None: return None
        return float(value)
    
    def getDeviceIsOn(self):
        value = self._getValueFromDevice(WRITE_IS_OUTPUT_ON)
        if value is None: return None
        return bool(value)

    def _getValueFromDevice(self, command):
        try:
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to get value with command:", command ,"when not connected to device")
                    return None
                DataAccess.sendValueToDevice(self.connection,command)
                acknowledgement = DataAccess.getResponseFromDevice(self.connection)
                self._verifyAcknowledgement(acknowledgement, command, data='')
                response = DataAccess.getResponseFromDevice(self.connection)
                self._verifyResponse(response, command, data='')
            return response.data
        except Exception as e:
            self.logger.exception(e)
            return None

    def _createConnection(self):
        return SerialConnection(
            baudrate = 9600,
            timeout = 0.1,
            logger = self.logger,
            idMessage = self._getDeviceIdMessage(),
            deviceVerificationFunc = self._deviceIdResponseFunction)

    def _registerUpdateFunction(self, func, condition):
        if condition not in self.updateParameters:
            self.updateParameters[condition] = [None,[]] #(Value, list_of_update_functions)
        self.updateParameters[condition][1].append(func)

    def _getDeviceUsbPortWorker(self, allUsbPorts):
        try:
            with self.connectionLock:
                if not allUsbPorts:
                    allUsbPorts = self.connection.availableConnections()
                defaultPort = None
                for port in allUsbPorts:
                    if self.connection.deviceOnPort(port):
                        defaultPort =  port
                        break
            if defaultPort:
                self.queue.put(_defaultUsbPortUpdate)
                self.queue.put(defaultPort) 
        except Exception as e: 
            self.logger.exception(e)

    def _updateAllValuesWorker(self):
        try:
            allValues = self.getAllValues()
            if allValues is None or len(allValues) < 7:
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
            self.logger.exception(e)
      
    def _updateStreamValueWorker(self):
        try:
            respondList = []
            with self.connectionLock:
                if not self.connected:
                    self.logger.debug("Trying to get stream values when not connected to device")
                    return
                response = DataAccess.getResponseFromDevice(self.connection)
                while response:
                    respondList.append()
                    response = DataAccess.getResponseFromDevice(self.connection)
            if not respondList: return
            commandDataList = [(x.command, x.data) for x in respondList]
            if commandDataList is None: return
            for pair in commandDataList:
                command = pair[0]
                value = pair[1]
                if command == WRITE_REAL_VOLTAGE:
                    self.queue.put(_realVoltageUpdate)
                    self.queue.put(float(value))
                elif command == WRITE_REAL_CURRENT:
                    self.queue.put(_realCurrentUpdate)      
                    self.queue.put(float(value))
                elif command == WRITE_PREREGULATOR_VOLTAGE:
                    self.queue.put(_preRegVoltageUpdate)      
                    self.queue.put(float(value))
                elif command == WRITE_TARGET_VOLTAGE:
                    self.queue.put(_targetVoltageUpdate)      
                    self.queue.put(float(value))
                elif command == WRITE_TARGET_CURRENT:
                    self.queue.put(_targetCurrentUpdate)      
                    self.queue.put(float(value))
                elif command == WRITE_IS_OUTPUT_ON:
                    self.queue.put(_outputOnOffUpdate)      
                    self.queue.put(float(value))
                elif command == WRITE_INPUT_VOLTAGE:
                    self.queue.put(_inputVoltageUpdate)      
                    self.queue.put(float(value))
        except Exception as e:    
            self.logger.exception(e)
                            
    def _connectWorker(self, usbPortNumber):
        try:
            self.queue.put(_connectUpdate)
            if usbPortNumber == '' or usbPortNumber is None:
                self.logger.debug("No usb port given")
                self.queue.put((0,_NO_USBPORT_SELECTED_STRING))
                return
            else:
                self.queue.put((0, _CONNECTING_STRING))
            self.connected = self.connect(usbPortNumber)
            self.queue.put(_connectUpdate)
            if self.connected:
                self.queue.put((1,_CONNECTED_STRING))
            else:
                self.queue.put((0,_NO_DEVICE_FOUND_STRING))         
        except:
            self.queue.put(_connectUpdate)
            self.queue.put((0,_NO_DEVICE_FOUND_STRING))
        
    def _connectionLost(self):
        self.connected = False
        self.queue.put(_connectUpdate)
        self.queue.put((0,_LOST_CONNECTION_STRING))
   
    def _addJobForLine(self, line, logToDataFile, filePath):
        self.queue.put(_scheduleNewLineUpdate)
        self.queue.put(line.rowNumber)
        self.setTargetVoltage(line.getVoltage())
        self.setTargetCurrent(line.getCurrent())
            
        if logToDataFile:
            self._logValuesToFile(filePath)
   
    def _resetDevice(self, startingTargetVoltage, startingTargetCurrent, startingOutputOn):
        self.setTargetVoltage(startingTargetVoltage)
        self.setTargetCurrent(startingTargetCurrent)
        self.setOutputOnOff(startingOutputOn)
        self.stopSchedule()
   
    def _startTimeIntervalLogging(self, loggingTimeInterval, filePath):
        time.sleep(1) # Sleep for one sec to account for the 1 sec time delay in jobs
        self.threadHelper.runIntervalJob(function = self._logValuesToFile, interval=loggingTimeInterval, args=[filePath])
        
    def _logValuesToFile(self,filePath):
        allValues = self.getAllValues()
        if allValues is None: return
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

    def _registerListeners(self):
        self.notifyRealCurrentUpdate(self._realCurrentUpdate)
        self.notifyRealVoltageUpdate(self._realVoltageUpdate)
        self.notifyTargetCurrentUpdate(self._targetCurrentUpdate)
        self.notifyTargetVoltageUpdate(self._targetVoltageUpdate)
        self.notifyInputVoltageUpdate(self._inputVoltageUpdate)
        self.notifyOutputUpdate(self._outPutOnOffUpdate)
        self.notifyPreRegVoltageUpdate(self._preRegVoltageUpdate)
        self.notifyConnectedUpdate(self._connectionUpdate)

    def _targetVoltageUpdate(self, newTargetVoltage):
        self.currentValues.targetVoltage = float(newTargetVoltage)

    def _inputVoltageUpdate(self, newInputVoltage):
        self.currentValues.inputVoltage = float(newInputVoltage)
    
    def _targetCurrentUpdate(self, newTargetCurrent):
        self.currentValues.targetCurrent = int(newTargetCurrent)
    
    def _realVoltageUpdate(self, newRealVoltage):
        self.currentValues.realVoltage = newRealVoltage
    
    def _realCurrentUpdate(self, newRealCurrent):
        self.currentValues.realCurrent = newRealCurrent
    
    def _outPutOnOffUpdate(self, newOutputOn):
        self.currentValues.outputOn = newOutputOn
    
    def _preRegVoltageUpdate(self, preRegVoltage):
        self.currentValues.preRegVoltage = preRegVoltage

    def _connectionUpdate(self, connected):
        if not connected:
            self.stopAutoUpdate()

    def _checkDeviceForAcknowledgement(self, command, data=''):
        try:
            deviceResponse = DataAccess.getResponseFromDevice(self.connection)
            self._verifyAcknowledgement(deviceResponse, command, data)
        except Exception as e:
            self.logger.exception(e)

    def _verifyResponse(self, response, command, data):
        self._verifyCrcCode(response, command, data)

    def _verifyAcknowledgement(self, acknowledgementResponse, command, data):
        if not acknowledgementResponse:
            raise Exception("No response from device")
            self._logSendingDataToDevice(command, data)
        if acknowledgementResponse.command == NOTACKNOWLEDGE:
            self._logTransmissionError("Received NAK from device", command, data, acknowledgementResponse)
        elif acknowledgementResponse.command != ACKNOWLEDGE:
            self._logTransmissionError("Received neither AK nor NAK from device", command, data, acknowledgementResponse)
        else:
            self._verifyCrcCode(acknowledgementResponse, command, data)

    def _logTransmissionError(self, errorMessage, sendingCommand, sendingData, response):
        self.logger.error(errorMessage)
        self._logSendingDataToDevice(sendingCommand, sendingData)
        self._logReceivingDeviceData(response)
 
    def _logSendingDataToDevice(self, command, data):
        sendingData = DeviceCommunication.toReadableSerial(command, data)
        self.logger.error("Data sent to device: %s" % ''.join(sendingData))

    def _logReceivingDeviceData(self, deviceResponse):
        self.logger.error("Data received from device: %s" % ''.join(deviceResponse.readableSerial))

    def _verifyCrcCode(self,response, command, data):
        """ 
        Take data from the responses and create crc code like I was sending them
        to the device. Then compare the generated crc code with the crc code from device
        """
        expectedCrcCode = Crc16.create(response.command, response.rawData) 
        if response.crc != expectedCrcCode:
            self._logTransmissionError("Unexpected crc code from device", command, data, response)
    
    """
    Gives the messages needed to send to device to verify that device is using a given port
    """
    def _getDeviceIdMessage(self):
        return DeviceCommunication.toSerial(HANDSHAKE, data='')
    
    """
    Function used to verify an id response from device, i.e. if the reponse come from our device or not
    """
    def _deviceIdResponseFunction(self, serialResponse):
        try:      
            reseponse = DeviceCommunication.fromSerial(serialResponse)
            return reseponse.command == ACKNOWLEDGE
        except Exception as e:
            return False 
