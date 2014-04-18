import serial
import glob
import threading
from PsController.Model.Constants import *
import PsController.Utilities.OsHelper as osHelper


class SerialConnection():
    def __init__(
            self,
            baudRate,
            timeout,
            logger,
            idMessage,
            deviceVerificationFunc):
        self.baudRate = baudRate
        self.timeout = timeout
        self.processLock = threading.Lock()
        self.logger = logger
        self.idMessage = idMessage
        self.deviceVerificationFunc = deviceVerificationFunc
        self.connectNotificationFunctionList = []
        self.connected = False
        self.connection = None

    def availableConnections(self):
        """Get available usb ports"""
        systemType = osHelper.getCurrentOs()
        available = []
        usbList = []
        if systemType == osHelper.WINDOWS:
            usbList = range(256)
        elif systemType == osHelper.OSX:
            usbList = glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
        elif systemType == osHelper.LINUX:
            usbList = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')

        for port in usbList:
            try:
                con = serial.Serial(port, self.baudRate, timeout=0.01)
                available.append(con.portstr)
                con.close()
            except serial.SerialException:
                pass
        return available

    def connect(self, usbPort):
        self.connected = self.deviceOnPort(usbPort)
        if self.connected:
            self.connection = serial.Serial(usbPort, self.baudRate, timeout=self.timeout)
        return self.connected

    def disconnect(self):
        self.connection.close()
        self.connected = False

    def connected(self):
        return self.connected

    def clearBuffer(self):
        self.connection.flushInput()

    def deviceOnPort(self, usbPort):
        logString = "Checking if device is on port " + usbPort
        self.logger.info(logString)
        try:
            tempConnection = serial.Serial(usbPort, self.baudRate, timeout=self.timeout)
            self._sendToDevice(tempConnection, self.idMessage)
            deviceResponse = self._readDeviceResponse(tempConnection)
            return self.deviceVerificationFunc(deviceResponse)
        except:
            logString = "Device not found on port " + usbPort
            self.logger.info(logString)

    def notifyOnConnectionLost(self, func):
        self.connectNotificationFunctionList.append(func)

    def get(self):
        if not self.connected:
            return
        try:
            serialResponse = self._readDeviceResponse(self.connection)
            logString = "Serial data received:  %s" % serialResponse
            self.logger.debug(logString)
            return serialResponse
        except Exception:
            self.connected = False
            self._notifyConnectionLost()
            raise Exception("Error when reading value from device.")

    def set(self, sendingData):
        if not self.connected:
            return
        try:
            self.logger.debug("Serial data sent:%s" % sendingData)
            self._sendToDevice(self.connection, sendingData)
        except serial.SerialTimeoutException:
            self.connected = False
            self._notifyConnectionLost()
            raise Exception("Error when setting value with data: %s ", sendingData)

    def _sendToDevice(self, serialConnection, data):
        with self.processLock:
            serialConnection.write(data)

    def _readDeviceResponse(self, serialConnection):
        with self.processLock:
            serialResponse = self._readLine(serialConnection)
        return serialResponse

    @staticmethod
    def _readLine(serialConnection):
        """Custom readLine method to avoid end of line char issues"""
        line = bytearray()
        startCount = 0
        while True:
            c = serialConnection.read(1)
            if c:
                line += c
            else:
                break

            if c[0] == START:
                startCount += 1
            if startCount == 2:
                break
        return bytes(line)

    def _notifyConnectionLost(self):
        for func in self.connectNotificationFunctionList:
            func()

    def currentConnectedUsbPort(self):
        return self.connection.port
