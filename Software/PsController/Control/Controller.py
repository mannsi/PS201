import queue
import threading
import logging
import uuid
import time
from datetime import datetime, timedelta

import PsController.Model.Constants as ModelConstants
from PsController.Model.DeviceValues import DeviceValues
from PsController.Model.Constants import *
from PsController.Utilities.Crc import Crc16
from PsController.Utilities.ThreadHelper import ThreadHelper
from . import Constants


class Controller:
    def __init__(self, Model, threaded=False):
        self._Model = Model
        self._threaded = threaded
        self._transactionLock = threading.Lock()
        self._updateQueue = queue.Queue()

        # A dict with key: UpdateCondition and value (currentConditionValue, listOfUpdateFunctions)
        self._updateFunctionsAndValues = {}

        self._controller = _ControllerLogic(self._Model, self._transactionLock, self._conditionUpdated)
        self._logHandlersAdded = False
        self.setLogging(logging.ERROR)
        self._autoUpdateScheduler = None
        self._pollDeviceScheduler = None
        self._registerListeners()
        self._forcedUsbPort = None

    @property
    def connected(self):
        return self._Model.connected

    def connect(self, forcedUsbPort=''):
        self._forcedUsbPort = forcedUsbPort
        if self._threaded:
            ThreadHelper.runThreadedJob(self._connectWorker, [forcedUsbPort])
        else:
            try:
                with self._transactionLock:
                    self._Model.connect(forcedUsbPort)
                    return self.connected
            except:
                logging.getLogger(ModelConstants.LOGGER_NAME).error("Error while connecting to device")
                return False

    def _connectWorker(self, forcedUsbPort):
        print("Trying to connect ...")
        try:
            self._Model.connect(forcedUsbPort)
            if self.connected:
                self._conditionUpdated(Constants.CONNECT_UPDATE, ModelConstants.CONNECTED)
            else:
                self._conditionUpdated(Constants.CONNECT_UPDATE, ModelConstants.NO_DEVICE_FOUND)
        except Exception as e:
            logging.getLogger(ModelConstants.LOGGER_NAME).error('Error connecting to device. Msg', str(e))

    def disconnect(self):
        try:
            self._Model.disconnect()
        except Exception as e:
            logging.getLogger(ModelConstants.LOGGER_NAME).error('Error disconnecting from device. Msg', str(e))
        self._conditionUpdated(Constants.CONNECT_UPDATE, ModelConstants.DISCONNECTED)
        self._conditionUpdated(Constants.OUTPUT_VOLTAGE_UPDATE, 0)
        self._conditionUpdated(Constants.OUTPUT_CURRENT_UPDATE, 0)
        self._conditionUpdated(Constants.TARGET_VOLTAGE_UPDATE, 0)
        self._conditionUpdated(Constants.TARGET_CURRENT_UPDATE, 0)
        self._conditionUpdated(Constants.PRE_REG_VOLTAGE_UPDATE, 0)
        self._conditionUpdated(Constants.INPUT_VOLTAGE_UPDATE, 0)
        self._conditionUpdated(Constants.OUTPUT_ON_OFF_UPDATE, 0)

    def setTargetVoltage(self, targetVoltage):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.setTargetVoltage, [targetVoltage, self._threaded])
        else:
            self._controller.setTargetVoltage(targetVoltage, self._threaded)

    def setTargetCurrent(self, targetCurrent):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.setTargetCurrent, [targetCurrent, self._threaded])
        else:
            self._controller.setTargetCurrent(targetCurrent, self._threaded)

    def setOutputOnOff(self, shouldBeOn):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.setOutputOnOff, [shouldBeOn, self._threaded])
        else:
            self._controller.setOutputOnOff(shouldBeOn, self._threaded)

    def getAllValues(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getAllValues, [True])
        else:
            return self._controller.getAllValues()

    def getOutputVoltage(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getOutputVoltage, [True])
        else:
            return self._controller.getOutputVoltage()

    def getOutputCurrent(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getOutputCurrent, [True])
        else:
            return self._controller.getOutputCurrent()

    def getPreRegulatorVoltage(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getPreRegulatorVoltage, [True])
        else:
            return self._controller.getPreRegulatorVoltage()

    def getTargetVoltage(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getTargetVoltage, [True])
        else:
            return self._controller.getTargetVoltage()

    def getTargetCurrent(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getTargetCurrent, [True])
        else:
            return self._controller.getTargetCurrent()

    def getInputVoltage(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getInputVoltage, [True])
        else:
            return self._controller.getInputVoltage()

    def getDeviceIsOn(self):
        if self._threaded:
            ThreadHelper.runThreadedJob(self._controller.getDeviceIsOn, [True])
        else:
            return self._controller.getDeviceIsOn()

    def setLogging(self, logLevel):
        if not self._logHandlersAdded:
            logger = logging.getLogger(ModelConstants.LOGGER_NAME)
            logger.propagate = False
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fileHandler = logging.FileHandler("PS201.log")
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
            printHandler = logging.StreamHandler()
            printHandler.setFormatter(formatter)
            logger.addHandler(printHandler)
            self._logHandlersAdded = True

            # Overwhelming when this is set to debug
            logging.getLogger("apscheduler.scheduler").setLevel(logging.ERROR)

        logging.getLogger(ModelConstants.LOGGER_NAME).setLevel(logLevel)

    def notifyConnectedUpdate(self, func):
        """Runs the func function when connection status changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.CONNECT_UPDATE)

    def notifyOutputCurrentUpdate(self, func):
        """Runs the func function when output current value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.OUTPUT_CURRENT_UPDATE)

    def notifyOutputVoltageUpdate(self, func):
        """Runs the func function when output voltage value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.OUTPUT_VOLTAGE_UPDATE)

    def notifyPreRegVoltageUpdate(self, func):
        """Runs the func function when pre reg voltage value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.PRE_REG_VOLTAGE_UPDATE)

    def notifyTargetCurrentUpdate(self, func):
        """Runs the func function when target current value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.TARGET_CURRENT_UPDATE)

    def notifyTargetVoltageUpdate(self, func):
        """Runs the func function when target voltage value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.TARGET_VOLTAGE_UPDATE)

    def notifyInputVoltageUpdate(self, func):
        """Runs the func function when input voltage value changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.INPUT_VOLTAGE_UPDATE)

    def notifyOutputUpdate(self, func):
        """Runs the func function when output setting changes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.OUTPUT_ON_OFF_UPDATE)

    def notifyScheduleDoneUpdate(self, func):
        """Runs the func function when a schedule finishes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.SCHEDULE_DONE_UPDATE)

    def notifyScheduleLineUpdate(self, func):
        """Runs the func function when the currently running schedule line finishes.
           Only runs when running in threaded mode"""
        self._registerUpdateFunction(func, Constants.SCHEDULE_NEW_LINE_UPDATE)

    def uiPulse(self):
        """A call to this function lets the controller know that the UI is ready to receive updates"""
        try:
            while self._updateQueue.qsize():
                updateCondition = self._updateQueue.get(0)
                updatedValue = self._updateQueue.get(0)
                value, updateFunctions = self._updateFunctionsAndValues[updateCondition]
                if value != updatedValue:
                    self._updateFunctionsAndValues[updateCondition][0] = updatedValue
                    for func in updateFunctions:
                        func(updatedValue)
        except queue.Empty:
            self._updateQueue.queue.clear()

    def startSchedule(self,
                      lines,
                      endingTargetVoltage,
                      endingTargetCurrent,
                      endingOutputOn,
                      logWhenValuesChange=False,
                      filePath=None,
                      useLoggingTimeInterval=False,
                      loggingTimeInterval=0):
        return self._controller.startSchedule(
            lines,
            endingTargetVoltage,
            endingTargetCurrent,
            endingOutputOn,
            logWhenValuesChange,
            filePath,
            useLoggingTimeInterval,
            loggingTimeInterval)

    def stopSchedule(self):
        self._controller.stopSchedule()

    def startAutoUpdate(self, interval):
        if self.connected:
            self._controller.startStream()
            ThreadHelper.runThreadedJob(self._controller.getAllValues, args=[True])
            self._autoUpdateScheduler = ThreadHelper.runIntervalJob(self._controller.getStreamValues, interval)

    def stopAutoUpdate(self):
        if self.connected:
            self._controller.stopStream()
        if self._autoUpdateScheduler:
            try:
                self._autoUpdateScheduler.shutdown(wait=False)
            except Exception as e:
                logging.getLogger(ModelConstants.LOGGER_NAME).exception(e)

    def _registerUpdateFunction(self, func, condition):
        if condition not in self._updateFunctionsAndValues:
            self._updateFunctionsAndValues[condition] = [None, []]  # [CurrentValue, ListOfUpdateFunctions]
        self._updateFunctionsAndValues[condition][1].append(func)

    def _conditionUpdated(self, condition, value):
        # Add to update queue if anybody is listening for the update
        if condition in self._updateFunctionsAndValues:
            self._updateQueue.put(condition)
            self._updateQueue.put(value)

    def _registerListeners(self):
        self._Model.notifyOnConnectionLost(self._connectionLost)
        self.notifyConnectedUpdate(self._connectionUpdateListener)

    def _connectionUpdateListener(self, connected):
        connected = (connected == ModelConstants.CONNECTED)
        if connected:
            logging.getLogger(ModelConstants.LOGGER_NAME).info("Device connected")
            self._stopPollForDevice()
            self.startAutoUpdate(interval=1/2)
        else:
            logging.getLogger(ModelConstants.LOGGER_NAME).info("Device disconnected")
            self.stopAutoUpdate()
            self._startPollForDevice()

    def _connectionLost(self):
        self._conditionUpdated(Constants.CONNECT_UPDATE, ModelConstants.DISCONNECTED)

    def _startPollForDevice(self):
        if self._pollDeviceScheduler is None or not self._pollDeviceScheduler.running:
            logging.getLogger(ModelConstants.LOGGER_NAME).debug("turning on poll device sched")
            self._pollDeviceScheduler = ThreadHelper.runIntervalJob(
                function=self.connect, interval=3, args=[self._forcedUsbPort])

    def _stopPollForDevice(self):
        if self._pollDeviceScheduler is not None:
            logging.getLogger(ModelConstants.LOGGER_NAME).debug("shutting down poll device sched")
            self._pollDeviceScheduler.shutdown(wait=False)


class _ControllerLogic():
    def __init__(self, Model, transactionLock, updateConditionFunction):
        self._Model = Model
        self._transactionLock = transactionLock
        self._updateConditionFunction = updateConditionFunction
        self._threadHelper = ThreadHelper()

    def startStream(self):
        with self._transactionLock:
            self._sendValueToDevice(START_STREAM)
            self._checkDeviceForAcknowledgement(START_STREAM)

    def stopStream(self):
        with self._transactionLock:
            self._sendValueToDevice(STOP_STREAM)
            self._checkDeviceForAcknowledgement(STOP_STREAM)

    def setTargetVoltage(self, targetVoltage, threaded=False):
        with self._transactionLock:
            self._sendValueToDevice(READ_TARGET_VOLTAGE, targetVoltage)
            self._checkDeviceForAcknowledgement(READ_TARGET_VOLTAGE)
        if threaded:
            self._updateConditionFunction(Constants.TARGET_VOLTAGE_UPDATE, targetVoltage)

    def setTargetCurrent(self, targetCurrent, threaded=False):
        with self._transactionLock:
            self._sendValueToDevice(READ_TARGET_CURRENT, targetCurrent)
            self._checkDeviceForAcknowledgement(READ_TARGET_CURRENT)
        if threaded:
            self._updateConditionFunction(Constants.TARGET_CURRENT_UPDATE, targetCurrent)

    def setOutputOnOff(self, shouldBeOn, threaded=False):
        setValue = TURN_OFF_OUTPUT
        if shouldBeOn:
            setValue = TURN_ON_OUTPUT
        with self._transactionLock:
            self._sendValueToDevice(setValue, shouldBeOn)
            self._checkDeviceForAcknowledgement(setValue)
        if threaded:
            self._updateConditionFunction(Constants.OUTPUT_ON_OFF_UPDATE, True)

    def getAllValues(self, threaded=False):
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

            if threaded:
                self._updateConditionFunction(Constants.OUTPUT_VOLTAGE_UPDATE, deviceValues.outputVoltage)
                self._updateConditionFunction(Constants.OUTPUT_CURRENT_UPDATE, deviceValues.outputCurrent)
                self._updateConditionFunction(Constants.TARGET_VOLTAGE_UPDATE, deviceValues.targetVoltage)
                self._updateConditionFunction(Constants.TARGET_CURRENT_UPDATE, deviceValues.targetCurrent)
                self._updateConditionFunction(Constants.PRE_REG_VOLTAGE_UPDATE, deviceValues.preRegVoltage)
                self._updateConditionFunction(Constants.INPUT_VOLTAGE_UPDATE, deviceValues.inputVoltage)
                self._updateConditionFunction(Constants.OUTPUT_ON_OFF_UPDATE, deviceValues.outputOn)
            else:
                return deviceValues
        except:
            logging.getLogger(LOGGER_NAME).error("Unable to get all values from device")

    def _handleReturnFloatValue(self, value, threaded, updateType):
        if value is None or value == '':
            returnValue = None
        else:
            returnValue = float(value)
        if threaded:
            self._updateConditionFunction(updateType, returnValue)
        else:
            return returnValue

    def getOutputVoltage(self, threaded=False):
        value = self._getValueFromDevice(WRITE_OUTPUT_VOLTAGE)
        return self._handleReturnFloatValue(value, threaded, Constants.OUTPUT_VOLTAGE_UPDATE)

    def getOutputCurrent(self, threaded=False):
        value = self._getValueFromDevice(WRITE_OUTPUT_CURRENT)
        return self._handleReturnFloatValue(value, threaded, Constants.OUTPUT_CURRENT_UPDATE)

    def getPreRegulatorVoltage(self, threaded=False):
        value = self._getValueFromDevice(WRITE_PRE_REGULATOR_VOLTAGE)
        return self._handleReturnFloatValue(value, threaded, Constants.PRE_REG_VOLTAGE_UPDATE)

    def getTargetVoltage(self, threaded=False):
        value = self._getValueFromDevice(WRITE_TARGET_VOLTAGE)
        return self._handleReturnFloatValue(value, threaded, Constants.TARGET_VOLTAGE_UPDATE)

    def getTargetCurrent(self, threaded=False):
        value = self._getValueFromDevice(WRITE_TARGET_CURRENT)
        return self._handleReturnFloatValue(value, threaded, Constants.TARGET_CURRENT_UPDATE)

    def getInputVoltage(self, threaded=False):
        value = self._getValueFromDevice(WRITE_INPUT_VOLTAGE)
        return self._handleReturnFloatValue(value, threaded, Constants.INPUT_VOLTAGE_UPDATE)

    def getDeviceIsOn(self, threaded=False):
        value = self._getValueFromDevice(WRITE_IS_OUTPUT_ON)
        if value is None or value == '':
            returnValue = None
        else:
            returnValue = bool(value)
        if threaded:
            self._updateConditionFunction(Constants.OUTPUT_ON_OFF_UPDATE, returnValue)
        else:
            return returnValue

    def startSchedule(self,
                      lines,
                      endingTargetVoltage,
                      endingTargetCurrent,
                      endingOutputOn,
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
        listOfArgs.append([endingTargetVoltage, endingTargetCurrent, endingOutputOn])
        self._threadHelper.runSchedule(listOfFunctions, listOfFiringTimes, listOfArgs, useLoggingTimeInterval,
                                       loggingTimeInterval, filePath, self._logValuesToFile)
        return True

    def stopSchedule(self):
        self._updateConditionFunction(Constants.SCHEDULE_DONE_UPDATE, uuid.uuid4())  # Fake a change event
        self._threadHelper.stopSchedule()
        self._resetScheduleLineParameter()

    def _resetScheduleLineParameter(self):
        # Resetting the current update value.
        # Done for the special case of a single line sequence is run twice which would not re trigger the event
        self._updateConditionFunction(Constants.SCHEDULE_NEW_LINE_UPDATE, -1)

    def _getValueFromDevice(self, command):
        with self._transactionLock:
            self._sendValueToDevice(command)
            acknowledgement = self._getDeviceResponse()
            _ControllerLogic._verifyAcknowledgement(acknowledgement, command, data='')
            response = self._getDeviceResponse()
            _ControllerLogic._verifyResponse(response, command, data='')
        return response.data

    def getStreamValues(self):
        """ This function is always run async
        """
        try:
            respondList = []
            with self._transactionLock:
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
                    self._updateConditionFunction(Constants.OUTPUT_VOLTAGE_UPDATE, float(value))
                elif command == WRITE_OUTPUT_CURRENT:
                    self._updateConditionFunction(Constants.OUTPUT_CURRENT_UPDATE, float(value))
                elif command == WRITE_PRE_REGULATOR_VOLTAGE:
                    self._updateConditionFunction(Constants.PRE_REG_VOLTAGE_UPDATE, float(value))
                elif command == WRITE_TARGET_VOLTAGE:
                    self._updateConditionFunction(Constants.TARGET_VOLTAGE_UPDATE, float(value))
                elif command == WRITE_TARGET_CURRENT:
                    self._updateConditionFunction(Constants.TARGET_CURRENT_UPDATE, float(value))
                elif command == WRITE_IS_OUTPUT_ON:
                    self._updateConditionFunction(Constants.OUTPUT_ON_OFF_UPDATE, float(value))
                elif command == WRITE_INPUT_VOLTAGE:
                    self._updateConditionFunction(Constants.INPUT_VOLTAGE_UPDATE, float(value))
        except Exception as e:
            logging.getLogger(LOGGER_NAME).exception(e)

    def _addJobForLine(self, line, logToDataFile, filePath):
        self._updateConditionFunction(Constants.SCHEDULE_NEW_LINE_UPDATE, line.rowNumber)
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

    def _checkDeviceForAcknowledgement(self, command, data=''):
        deviceResponse = self._getDeviceResponse()
        self._verifyAcknowledgement(deviceResponse, command, data)

    @classmethod
    def _verifyResponse(cls, response, command, data):
        cls._verifyCrcCode(response, command, data)

    @classmethod
    def _verifyAcknowledgement(cls, acknowledgementResponse, command, data):
        if not acknowledgementResponse:
            cls._logSendingDataAsError(command, data)
            logString = "No response from device when sending '" + _ControllerLogic._readableCommand(command) + "'"
            logging.getLogger(LOGGER_NAME).error(logString)
        elif acknowledgementResponse.command == NOT_ACKNOWLEDGE:
            logString = "Received 'NOT ACKNOWLEDGE' from device." \
                        "Command sent to device: '" + _ControllerLogic._readableCommand(command) + "'"
            cls._logTransmissionError(logString, command, data, acknowledgementResponse)
        elif acknowledgementResponse.command != ACKNOWLEDGE:
            logString = "Received neither 'ACKNOWLEDGE' nor 'NOT ACKNOWLEDGE' from device. " \
                        "Command sent to device: '" + _ControllerLogic._readableCommand(command) + "'"
            cls._logTransmissionError(logString, command, data, acknowledgementResponse)
        else:
            cls._verifyCrcCode(acknowledgementResponse, command, data)

    @classmethod
    def _logTransmissionError(cls, errorMessage, sendingCommand, sendingData, response):
        logging.getLogger(LOGGER_NAME).error(errorMessage)
        cls._logSendingDataAsError(sendingCommand, sendingData)
        cls._logReceivingDeviceData(response)

    @classmethod
    def _logSendingDataAsError(cls, command, data):
        logString = "Command " + _ControllerLogic._readableCommand(command) + " sent to device with data " + data
        logging.getLogger(LOGGER_NAME).error(logString)

    @staticmethod
    def _logReceivingDeviceData(deviceResponse):
        logging.getLogger(LOGGER_NAME).error("Data received from device: %s" % ''.join(deviceResponse.readableSerial))

    @classmethod
    def _verifyCrcCode(cls, response, command, data):
        """
        Take data from the responses and create crc code like I was sending them
        to the device. Then compare the generated crc code with the crc code from device
        """
        expectedCrcCode = Crc16.create(response.command, response.rawData)
        if response.crc != expectedCrcCode:
            errorText = "Unexpected crc code from device. Got ", response.crc, " but expected ", expectedCrcCode
            cls._logTransmissionError(errorText, command, data, response)

    def _getDeviceResponse(self):
        try:
            deviceResponse = self._Model.getResponseFromDevice()
            if deviceResponse is not None:
                logString = "Got response command '" + _ControllerLogic._readableCommand(deviceResponse.command) + \
                            "' with data '" + deviceResponse.data + "' from device"
                logging.getLogger(LOGGER_NAME).info(logString)
            return deviceResponse
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error("Error getting response from device. Error message: " + str(e))

    def _sendValueToDevice(self, command, data=''):
        logString = "Sending command '" + _ControllerLogic._readableCommand(command) + \
                    "' with data '" + str(data) + "' to device"
        logging.getLogger(LOGGER_NAME).info(logString)
        try:
            # Clear buffer so that the acknowledge check does not meet a stream value previously in the buffer
            self._Model.clearBuffer()
            self._Model.sendValueToDevice(command, data)
        except:
            logging.getLogger(LOGGER_NAME).error('Error sending command ', _ControllerLogic._readableCommand(command),
                                                 ' with data: ', data, ' to device')

    @staticmethod
    def _readableCommand(command):
        if command == WRITE_OUTPUT_VOLTAGE:
            return "Write output voltage"
        elif command == WRITE_OUTPUT_CURRENT:
            return "Write output current"
        elif command == WRITE_INPUT_VOLTAGE:
            return "Write input voltage"
        elif command == WRITE_PRE_REGULATOR_VOLTAGE:
            return "Write pre req voltage"
        elif command == WRITE_ALL:
            return "Write all"
        elif command == WRITE_IS_OUTPUT_ON:
            return "Write is output on"
        elif command == WRITE_TARGET_VOLTAGE:
            return "Write target voltage"
        elif command == WRITE_TARGET_CURRENT:
            return "Write target current"
        elif command == READ_TARGET_VOLTAGE:
            return "Read target voltage"
        elif command == READ_TARGET_CURRENT:
            return "Read target current"
        elif command == TURN_ON_OUTPUT:
            return "Turn output on"
        elif command == TURN_OFF_OUTPUT:
            return "Turn output off"
        elif command == START_STREAM:
            return "Start stream"
        elif command == STOP_STREAM:
            return "Stop stream"
        elif command == ACKNOWLEDGE:
            return "ACKNOWLEDGE"
        elif command == NOT_ACKNOWLEDGE:
            return "NOT_ACKNOWLEDGE"