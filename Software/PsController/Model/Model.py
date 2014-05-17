import logging

from PsController.Model.Constants import *
from .DataMapping.SerialDataMapping import SerialDataMapping
from .Connection.SerialConnectionFactory import SerialConnectionFactory


class Model:
    def __init__(self):
        self.connected = False
        self._dataAccessClass = SerialDataMapping()
        self._connection = SerialConnectionFactory(logger=logging.getLogger(LOGGER_NAME)).getConnection()
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

    def _notifyConnectionLost(self):
        for func in self._connectNotificationFunctionList:
            func()