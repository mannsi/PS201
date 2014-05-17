# TODO Need to register all the things somehow. Now they are all hardcoded which sucks
# TODO separate sequence logic from 'normal' logic

import logging
import queue
import threading

from PsController.Control.Controller import Controller
from PsController.Utilities.ThreadHelper import ThreadHelper
import PsController.Model.Constants as ModelConstants
from . import Constants


class Control:
    """
    Public control interface
    """
    def __init__(self, Model, threaded=False):
        self._Model = Model
        self._threaded = threaded
        self._transactionLock = threading.Lock()
        self._updateQueue = queue.Queue()

        # A dict with key: UpdateCondition and value (currentConditionValue, listOfUpdateFunctions)
        self._updateFunctionsAndValues = {}

        # TODO this should not be created here. It should come from a factory or as a parameter or something
        self._controller = Controller(self._Model, self._transactionLock, self._conditionUpdated)
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