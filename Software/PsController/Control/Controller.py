import logging
import uuid
import time
from datetime import datetime, timedelta
from PsController.Model.DeviceValues import DeviceValues
from PsController.Model.Constants import *
from PsController.Utilities.Crc import Crc16
#from PsController.DAL.SerialMapping import SerialMapping
from PsController.Utilities.ThreadHelper import ThreadHelper
from . import Constants


class Controller():
    def __init__(self, DAL, transactionLock, updateConditionFunction):
        self._DAL = DAL
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
                self._updateConditionFunction(Constants.PREREG_VOLTAGE_UPDATE, deviceValues.preRegVoltage)
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
        return self._handleReturnFloatValue(value, threaded, Constants.PREREG_VOLTAGE_UPDATE)

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
            Controller._verifyAcknowledgement(acknowledgement, command, data='')
            response = self._getDeviceResponse()
            Controller._verifyResponse(response, command, data='')
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
                    self._updateConditionFunction(Constants.PREREG_VOLTAGE_UPDATE, float(value))
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
            logString = "No response from device when sending '" + Controller._readableCommand(command) + "'"
            logging.getLogger(LOGGER_NAME).error(logString)
        elif acknowledgementResponse.command == NOT_ACKNOWLEDGE:
            logString = "Received 'NOT ACKNOWLEDGE' from device." \
                        "Command sent to device: '" + Controller._readableCommand(command) + "'"
            cls._logTransmissionError(logString, command, data, acknowledgementResponse)
        elif acknowledgementResponse.command != ACKNOWLEDGE:
            logString = "Received neither 'ACKNOWLEDGE' nor 'NOT ACKNOWLEDGE' from device. " \
                        "Command sent to device: '" + Controller._readableCommand(command) + "'"
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
        logString = "Command " + Controller._readableCommand(command) + " sent to device with data " + data
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
            deviceResponse = self._DAL.getResponseFromDevice()
            if deviceResponse is not None:
                logString = "Got response command '" + Controller._readableCommand(deviceResponse.command) + \
                            "' with data '" + deviceResponse.data + "' from device"
                logging.getLogger(LOGGER_NAME).info(logString)
            return deviceResponse
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error("Error getting response from device. Error message: " + str(e))

    def _sendValueToDevice(self, command, data=''):
        logString = "Sending command '" + Controller._readableCommand(command) + \
                    "' with data '" + str(data) + "' to device"
        logging.getLogger(LOGGER_NAME).info(logString)
        try:
            # Clear buffer so that the acknowledge check does not meet a stream value previously in the buffer
            self._DAL.clearBuffer()
            self._DAL.sendValueToDevice(command, data)
        except:
            logging.getLogger(LOGGER_NAME).error('Error sending command ', Controller._readableCommand(command),
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