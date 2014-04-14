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
from PsController.Utilities.DeviceResponse import DeviceCommunication, SerialException

_connectUpdate = "CONNECT"
_outputCurrentUpdate = "OUTPUT_CURRENT"
_outputVoltageUpdate = "OUTPUT_VOLTAGE"
_preRegVoltageUpdate = "PRE_REG_VOLTAGE"
_targetCurrentUpdate = "TARGET_CURRENT"
_targetVoltageUpdate = "TARGET_VOLTAGE"
_inputVoltageUpdate = "INPUT_VOLTAGE"
_outputOnOffUpdate = "OUTPUT_ON_OFF"
_scheduleDoneUpdate = "SCHEDULE_DONE"
_scheduleNewLineUpdate = "SCHEDULE_NEWLINE"
_defaultUsbPortUpdate = "DEFAULT_USB_PORT"

_CONNECTED_STRING = "Connected"
_DISCONNECTED_STRING = "Disconnected"
_CONNECTING_STRING = "Connecting ..."
_NO_DEVICE_FOUND_STRING = "No device found"
_NO_USB_PORT_SELECTED_STRING = "No usb port selected"
_LOST_CONNECTION_STRING = "Lost connection"


class Controller():
    def __init__(self):
        self.logger = None
        self.setLogging(logging.ERROR)
        self.connectionLock = threading.Lock()
        self._updateQueue = queue.Queue()
        self.threadHelper = ThreadHelper()
        self.updateParameters = {}  # A dict with key: UpdateCondition and value (conditionValue, listOfUpdateFunctions)
        self.connected = False
        self.currentValues = DeviceValues()
        self.connection = self._createConnection()
        self.connection.notifyOnConnectionLost(self._connectionLost)
        self._registerListeners()
        self.autoUpdateScheduler = None

    def connect(self, usbPortNumber, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self._connectWorker, [usbPortNumber])
        else:
            try:
                if usbPortNumber == '' or usbPortNumber is None:
                    self.logger.info("Empty usb port given")
                    return False
                with self.connectionLock:
                    self.connected = self.connection.connect(usbPortNumber)
                    return self.connected
            except Exception as e:
                self.logger.error("Device not found on given port")
                self.logger.exception(e)
                return False

    def disconnect(self):
        with self.connectionLock:
            self.connection.disconnect()

        # Notify UI of the disconnect update
        self._updateQueue.put(_connectUpdate)
        self._updateQueue.put((0, _DISCONNECTED_STRING))
        self._updateQueue.put(_outputVoltageUpdate)
        self._updateQueue.put(0.0)
        self._updateQueue.put(_outputCurrentUpdate)
        self._updateQueue.put(0)
        self._updateQueue.put(_targetVoltageUpdate)
        self._updateQueue.put(0.0)
        self._updateQueue.put(_targetCurrentUpdate)
        self._updateQueue.put(0)
        self._updateQueue.put(_preRegVoltageUpdate)
        self._updateQueue.put(0.0)
        self._updateQueue.put(_inputVoltageUpdate)
        self._updateQueue.put(0.0)
        self._updateQueue.put(_outputOnOffUpdate)
        self._updateQueue.put(0)

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
                for port in allUsbPorts:
                    if self.connection.deviceOnPort(port):
                        return port
                return None

    def setTargetVoltage(self, targetVoltage, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setTargetVoltage, args=[targetVoltage])
        else:
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to set voltage when not connected to device")
                    return
                self._sendValueToDevice(READ_TARGET_VOLTAGE, targetVoltage)
                self._checkDeviceForAcknowledgement(READ_TARGET_VOLTAGE)
            self._updateQueue.put(_targetVoltageUpdate)
            self._updateQueue.put(targetVoltage)

    def setTargetCurrent(self, targetCurrent, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setTargetCurrent, args=[targetCurrent])
        else:
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to set current when not connected to device")
                    return
                self._sendValueToDevice(READ_TARGET_CURRENT, targetCurrent)
                self._checkDeviceForAcknowledgement(READ_TARGET_CURRENT)
            self._updateQueue.put(_targetCurrentUpdate)
            self._updateQueue.put(targetCurrent)

    def setOutputOnOff(self, shouldBeOn, threaded=False):
        if threaded:
            self.threadHelper.runThreadedJob(self.setOutputOnOff, args=[shouldBeOn])
        else:
            setValue = TURN_OFF_OUTPUT
            if shouldBeOn:
                setValue = TURN_ON_OUTPUT
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to set output when not connected to device")
                    return
                self._sendValueToDevice(setValue, shouldBeOn)
                self._checkDeviceForAcknowledgement(setValue)
            self._updateQueue.put(_outputOnOffUpdate)
            self._updateQueue.put(shouldBeOn)

    def notifyConnectedUpdate(self, func):
        """Runs the func function when connection status is updated through auto update"""
        self._registerUpdateFunction(func, _connectUpdate)

    def notifyOutputCurrentUpdate(self, func):
        """Runs the func function when output current value changes through auto update"""
        self._registerUpdateFunction(func, _outputCurrentUpdate)

    def notifyOutputVoltageUpdate(self, func):
        """Runs the func function when output voltage value changes through auto update"""
        self._registerUpdateFunction(func, _outputVoltageUpdate)

    def notifyPreRegVoltageUpdate(self, func):
        """Runs the func function when pre reg voltage value changes through auto update"""
        self._registerUpdateFunction(func, _preRegVoltageUpdate)

    def notifyTargetCurrentUpdate(self, func):
        """Runs the func function when target current value changes through auto update"""
        self._registerUpdateFunction(func, _targetCurrentUpdate)

    def notifyTargetVoltageUpdate(self, func):
        """Runs the func function when target voltage value changes through auto update"""
        self._registerUpdateFunction(func, _targetVoltageUpdate)

    def notifyInputVoltageUpdate(self, func):
        """Runs the func function when input voltage value changes through auto update"""
        self._registerUpdateFunction(func, _inputVoltageUpdate)

    def notifyOutputUpdate(self, func):
        """Runs the func function when output setting changes through auto update"""
        self._registerUpdateFunction(func, _outputOnOffUpdate)

    def notifyScheduleDoneUpdate(self, func):
        """Runs the func function when a schedule finishes"""
        self._registerUpdateFunction(func, _scheduleDoneUpdate)

    def notifyScheduleLineUpdate(self, func):
        """Runs the func function when the currently running schedule line finishes"""
        self._registerUpdateFunction(func, _scheduleNewLineUpdate)

    def notifyDefaultUsbPortUpdate(self, func):
        """Runs the func function when the default usb port is updated """
        self._registerUpdateFunction(func, _defaultUsbPortUpdate)

    def uiPulse(self):
        """A call to this function lets the controller know that the UI is ready to receive updates"""
        try:
            while self._updateQueue.qsize():
                updateCondition = self._updateQueue.get(0)
                updatedValue = self._updateQueue.get(0)
                value, updateFunctions = self.updateParameters[updateCondition]
                if value != updatedValue:
                    self.updateParameters[updateCondition][0] = updatedValue
                    for func in updateFunctions:
                        func(updatedValue)
        except queue.Empty:
            self._updateQueue.queue.clear()

    def startAutoUpdate(self, interval, updateType):
        if updateType == 0:
            # Polling updates
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to start polling auto update when not connected to device")
                    return
                self.connection.clearBuffer()
                self._sendValueToDevice(STOP_STREAM)
                self._checkDeviceForAcknowledgement(STOP_STREAM)
            self.autoUpdateScheduler = self.threadHelper.runIntervalJob(self.updateAllValuesWorker, interval)
        elif updateType == 1:
            # Streaming updates
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to start streaming auto update when not connected to device")
                    return
                self._sendValueToDevice(START_STREAM)
                self._checkDeviceForAcknowledgement(START_STREAM)
                self.threadHelper.runThreadedJob(self.updateAllValuesWorker, args=[])
            self.autoUpdateScheduler = self.threadHelper.runIntervalJob(self._updateStreamValueWorker, interval)

    def stopAutoUpdate(self):
        if self.autoUpdateScheduler:
            try:
                self.autoUpdateScheduler.shutdown(wait=False)
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
        self.threadHelper.runSchedule(listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval,
                                      loggingTimeInterval, filePath, self._logValuesToFile)
        return True

    def stopSchedule(self):
        self._updateQueue.put(_scheduleDoneUpdate)
        self._updateQueue.put(uuid.uuid4())  # Add a random UUID to fake a change event
        self.threadHelper.stopSchedule()
        self._resetScheduleLineParameter()

    def _resetScheduleLineParameter(self):
        self.updateParameters[_scheduleNewLineUpdate][0] = -1

    def getAllValues(self):
        try:
            deviceResponse = self._getValueFromDevice(WRITE_ALL)
            if not deviceResponse:
                return
            splitValues = [float(x) for x in deviceResponse.split(";")]
            if len(splitValues) < 7:
                return None
            deviceValues = DeviceValues()
            deviceValues.outputVoltage = splitValues[0]
            deviceValues.outputCurrent = splitValues[1]
            deviceValues.targetVoltage = splitValues[2]
            deviceValues.targetCurrent = splitValues[3]
            deviceValues.preRegVoltage = splitValues[4]
            deviceValues.inputVoltage = splitValues[5]
            deviceValues.outputOn = splitValues[6]

            return deviceValues
        except Exception as e:
            self.logger.exception(e)

    def getOutputVoltage(self):
        value = self._getValueFromDevice(WRITE_OUTPUT_VOLTAGE)
        if value is None or value == '':
            return None
        return float(value)

    def getOutputCurrent(self):
        value = self._getValueFromDevice(WRITE_OUTPUT_CURRENT)
        if value is None or value == '':
            return None
        return float(value)

    def getPreRegulatorVoltage(self):
        value = self._getValueFromDevice(WRITE_PRE_REGULATOR_VOLTAGE)
        if value is None or value == '':
            return None
        return float(value)

    def getTargetVoltage(self):
        value = self._getValueFromDevice(WRITE_TARGET_VOLTAGE)
        if value is None or value == '':
            return None
        return float(value)

    def getTargetCurrent(self):
        value = self._getValueFromDevice(WRITE_TARGET_CURRENT)
        if value is None or value == '':
            return None
        return float(value)

    def getInputVoltage(self):
        value = self._getValueFromDevice(WRITE_INPUT_VOLTAGE)
        if value is None or value == '':
            return None
        return float(value)

    def getDeviceIsOn(self):
        value = self._getValueFromDevice(WRITE_IS_OUTPUT_ON)
        if value is None or value == '':
            return None
        return bool(value)

    def _getValueFromDevice(self, command):
        try:
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to get value with command:", command, "when not connected to device")
                    return None
                self._sendValueToDevice(command)
                acknowledgement = self._getDeviceResponse()
                self._verifyAcknowledgement(acknowledgement, command, data='')
                response = self._getDeviceResponse()
                self._verifyResponse(response, command, data='')
            return response.data
        except Exception as e:
            self.logger.exception(e)
            return None

    def _createConnection(self):
        return SerialConnection(
            baudRate=9600,
            timeout=0.1,
            logger=self.logger,
            idMessage=self._getDeviceIdMessage(),
            deviceVerificationFunc=self._deviceIdResponseFunction)

    def _registerUpdateFunction(self, func, condition):
        if condition not in self.updateParameters:
            self.updateParameters[condition] = [None, []]
        self.updateParameters[condition][1].append(func)

    def _getDeviceUsbPortWorker(self, allUsbPorts):
        try:
            with self.connectionLock:
                if not allUsbPorts:
                    allUsbPorts = self.connection.availableConnections()
                defaultPort = None
                for port in allUsbPorts:
                    if self.connection.deviceOnPort(port):
                        defaultPort = port
                        break
            if defaultPort:
                self._updateQueue.put(_defaultUsbPortUpdate)
                self._updateQueue.put(defaultPort)
        except Exception as e:
            self.logger.exception(e)

    def updateAllValuesWorker(self):
        try:
            deviceValues = self.getAllValues()
            if deviceValues is None:
                return
            self._updateQueue.put(_outputVoltageUpdate)
            self._updateQueue.put(deviceValues.outputVoltage)
            self._updateQueue.put(_outputCurrentUpdate)
            self._updateQueue.put(deviceValues.outputCurrent)
            self._updateQueue.put(_targetVoltageUpdate)
            self._updateQueue.put(deviceValues.targetVoltage)
            self._updateQueue.put(_targetCurrentUpdate)
            self._updateQueue.put(deviceValues.targetCurrent)
            self._updateQueue.put(_preRegVoltageUpdate)
            self._updateQueue.put(deviceValues.preRegVoltage)
            self._updateQueue.put(_inputVoltageUpdate)
            self._updateQueue.put(deviceValues.inputVoltage)
            self._updateQueue.put(_outputOnOffUpdate)
            self._updateQueue.put(deviceValues.outputOn)
        except Exception as e:
            self.logger.exception(e)

    def _updateStreamValueWorker(self):
        try:
            respondList = []
            with self.connectionLock:
                if not self.connected:
                    self.logger.info("Trying to get stream values when not connected to device")
                    return
                response = self._getDeviceResponse()
                while response:
                    respondList.append(response)
                    response = self._getDeviceResponse()
            if not respondList:
                return
            commandDataList = [(x.command, x.data) for x in respondList]
            if commandDataList is None:
                return
            for pair in commandDataList:
                command = pair[0]
                value = pair[1]
                if command == WRITE_OUTPUT_VOLTAGE:
                    self._updateQueue.put(_outputVoltageUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_OUTPUT_CURRENT:
                    self._updateQueue.put(_outputCurrentUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_PRE_REGULATOR_VOLTAGE:
                    self._updateQueue.put(_preRegVoltageUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_TARGET_VOLTAGE:
                    self._updateQueue.put(_targetVoltageUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_TARGET_CURRENT:
                    self._updateQueue.put(_targetCurrentUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_IS_OUTPUT_ON:
                    self._updateQueue.put(_outputOnOffUpdate)
                    self._updateQueue.put(float(value))
                elif command == WRITE_INPUT_VOLTAGE:
                    self._updateQueue.put(_inputVoltageUpdate)
                    self._updateQueue.put(float(value))
        except Exception as e:
            self.logger.exception(e)

    def _connectWorker(self, usbPortNumber):
        self._updateQueue.put(_connectUpdate)
        if usbPortNumber == '' or usbPortNumber is None:
            self.logger.info("No usb port given")
            self._updateQueue.put((0, _NO_USB_PORT_SELECTED_STRING))
            return
        else:
            self._updateQueue.put((0, _CONNECTING_STRING))
        self.connected = self.connect(usbPortNumber)
        self._updateQueue.put(_connectUpdate)
        if self.connected:
            self._updateQueue.put((1, _CONNECTED_STRING))
        else:
            self._updateQueue.put((0, _NO_DEVICE_FOUND_STRING))

    def _connectionLost(self):
        self.connected = False
        self._updateQueue.put(_connectUpdate)
        self._updateQueue.put((0, _LOST_CONNECTION_STRING))

    def _addJobForLine(self, line, logToDataFile, filePath):
        self._updateQueue.put(_scheduleNewLineUpdate)
        self._updateQueue.put(line.rowNumber)
        self.setTargetVoltage(line.getVoltage())
        self.setTargetCurrent(line.getCurrent())

        if logToDataFile:
            time.sleep(2)
            self._logValuesToFile(filePath)

    def _resetDevice(self, startingTargetVoltage, startingTargetCurrent, startingOutputOn):
        self.setTargetVoltage(startingTargetVoltage)
        self.setTargetCurrent(startingTargetCurrent)
        self.setOutputOnOff(startingOutputOn)
        self.stopSchedule()

    def _logValuesToFile(self, filePath):
        deviceValues = self.getAllValues()
        if deviceValues is None:
            return
        with open(filePath, "a") as file:
            fileString = str(datetime.now())
            fileString += "\t"
            fileString += str(deviceValues.outputVoltage)
            fileString += "\t"
            fileString += str(deviceValues.outputCurrent)
            fileString += "\n"
            file.write(fileString)

    def _registerListeners(self):
        self.notifyOutputCurrentUpdate(self._outputCurrentUpdate)
        self.notifyOutputVoltageUpdate(self._outputVoltageUpdate)
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

    def _outputVoltageUpdate(self, newOutputVoltage):
        self.currentValues.outputVoltage = newOutputVoltage

    def _outputCurrentUpdate(self, newOutputCurrent):
        self.currentValues.outputCurrent = newOutputCurrent

    def _outPutOnOffUpdate(self, newOutputOn):
        self.currentValues.outputOn = newOutputOn

    def _preRegVoltageUpdate(self, preRegVoltage):
        self.currentValues.preRegVoltage = preRegVoltage

    def _connectionUpdate(self, connected):
        if not connected:
            self.stopAutoUpdate()

    def _checkDeviceForAcknowledgement(self, command, data=''):
        try:
            deviceResponse = self._getDeviceResponse()
            self._verifyAcknowledgement(deviceResponse, command, data)
        except Exception as e:
            self.logger.exception(e)

    def _verifyResponse(self, response, command, data):
        self._verifyCrcCode(response, command, data)

    def _verifyAcknowledgement(self, acknowledgementResponse, command, data):
        if not acknowledgementResponse:
            self._logSendingDataToDevice(command, data)
            raise Exception("No response from device")
        if acknowledgementResponse.command == NOT_ACKNOWLEDGE:
            self._logTransmissionError("Received 'NOT ACKNOWLEDGE' from device", command, data, acknowledgementResponse)
        elif acknowledgementResponse.command != ACKNOWLEDGE:
            self._logTransmissionError("Received neither 'ACKNOWLEDGE' nor 'NOT ACKNOWLEDGE' from device", command,
                                       data, acknowledgementResponse)
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

    def _verifyCrcCode(self, response, command, data):
        """ 
        Take data from the responses and create crc code like I was sending them
        to the device. Then compare the generated crc code with the crc code from device
        """
        expectedCrcCode = Crc16.create(response.command, response.rawData)
        if response.crc != expectedCrcCode:
            errorText = "Unexpected crc code from device. Got ", response.crc, " but expected ", expectedCrcCode
            self._logTransmissionError(errorText, command, data, response)

    @staticmethod
    def _getDeviceIdMessage():
        """Gives the messages needed to send to device to verify that device is using a given port"""
        return DeviceCommunication.toSerial(HANDSHAKE, data='')

    def _deviceIdResponseFunction(self, serialResponse):
        """Function used to verify an id response from device, i.e. if the response come from our device or not"""
        try:
            if not serialResponse:
                self.logger.info("Did not receive an ACKNOWLEDGE response")
                return False
            response = DeviceCommunication.fromSerial(serialResponse)
            self.logger.info("Received %s", readableConstant(response.command))
            return response.command == ACKNOWLEDGE
        except SerialException:
            self.logger.info("Did not receive an ACKNOWLEDGE response")
            return False

    def _getDeviceResponse(self):
        deviceResponse = DataAccess.getResponseFromDevice(self.connection)
        if deviceResponse is not None:
            logString = "Got response command '" + readableConstant(deviceResponse.command) + "' with data '" \
                        + deviceResponse.data + "' from device"
            self.logger.info(logString)
        return deviceResponse

    def _sendValueToDevice(self, command, data=''):
        logString = "Sending command '" + readableConstant(command) + "' with data '" + str(data) + "' to device"
        self.logger.info(logString)
        DataAccess.sendValueToDevice(self.connection, command, data)