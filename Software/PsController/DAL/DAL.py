import logging

from PsController.Model.Constants import *
from .SerialConnection import SerialConnection
from .SerialMapping import SerialMapping
from .SerialDataAccess import SerialDataAccess


class DAL:
    def __init__(self):
        self.connected = False
        self._dataAccessClass = SerialDataAccess()
        self._connection = self._createConnection()
        self._currentUsbPort = None
        self._connectNotificationFunctionList = []

    def connect(self, forcedUsbPort=None):
        if forcedUsbPort:
            self._connection.connect(forcedUsbPort)
        else:
            availablePorts = self._connection.availableConnections()
            for port in availablePorts:
                if self._connection.deviceOnPort(port):
                    self._currentUsbPort = port
                    self.connected = self._connection.connect(port)
                    break
        return self._connection.connected

    def disconnect(self):
        try:
            self._connection.disconnect()
        except Exception as e:
            print(e)

    def sendValueToDevice(self, command, data=''):
        try:
            self._dataAccessClass.sendValueToDevice(self._connection, command, data)
        except:
            self.connected = False
            self._notifyConnectionLost()
            raise Exception("Error when setting value")

    def getResponseFromDevice(self):
        try:
            return self._dataAccessClass.getResponseFromDevice(self._connection)
        except Exception:
            self.connected = False
            self._notifyConnectionLost()
            raise Exception("Error when reading value from device.")

    def clearBuffer(self):
        self._connection.clearBuffer()

    def notifyOnConnectionLost(self, func):
        self._connectNotificationFunctionList.append(func)

    def _createConnection(self):
        return SerialConnection(
            baudRate=9600,
            timeout=0.1,
            logger=logging.getLogger(LOGGER_NAME),
            idMessage=DAL._getDeviceIdMessage(),
            deviceVerificationFunc=self._deviceIdResponseFunction)

    @staticmethod
    def _getDeviceIdMessage():
        """Gives the messages needed to send to device to verify that device is using a given port"""
        return SerialMapping.toSerial(HANDSHAKE, data='')

    @staticmethod
    def _deviceIdResponseFunction(serialResponse):
        """Function used to verify an id response from device, i.e. if the response come from our device or not"""
        try:
            if not serialResponse:
                logging.getLogger(LOGGER_NAME).info("Did not receive an ACKNOWLEDGE response")
                return False
            response = SerialMapping.fromSerial(serialResponse)
            return response.command == ACKNOWLEDGE
        except:
            logging.getLogger(LOGGER_NAME).info("Did not receive an ACKNOWLEDGE response")
            return False

    def _notifyConnectionLost(self):
        for func in self._connectNotificationFunctionList:
            func()