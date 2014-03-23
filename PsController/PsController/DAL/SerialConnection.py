import serial
import platform
import glob
import threading
from PsController.Model.Constants import *

class SerialConnection():
    def __init__(
                 self, 
                 baudrate, 
                 timeout,  
                 logger,
                 idMessage,
                 deviceVerificationFunc):
        self.baudRate = baudrate
        self.timeout = timeout
        self.processLock = threading.Lock()
        self.logger = logger
        self.idMessage = idMessage
        self.deviceVerificationFunc = deviceVerificationFunc
        
    """
    Get a availableUsbPorts
    """
    def availableConnections(self):
        system_name = platform.system()
        available = []
        if system_name == "Windows":
            # Scan for available ports.
            usbList =  range(256)
        elif system_name == "Darwin":
            # Mac
            usbList = glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
        else:
            # Assume Linux or something else
            usbList = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
            
        for port in usbList:
            try:
                con = serial.Serial(port, self.baudRate, timeout = 0.01)
                available.append(con.portstr)
                con.close()
            except serial.SerialException:
                pass
        return available
    
    def connect(self, usbPort):
        self.connection = serial.Serial(usbPort, self.baudRate, timeout = self.timeout)
    
    def disconnect(self):
        self.connection.close()
     
    def get(self, sendingData=""):
        try:
            if sendingData:
                self._sendToDevice(self.connection, sendingData)
            serialResponse = self._readDeviceReponse(self.connection)
            logString = "Received:  %s" % serialResponse
            if sendingData:
                logString = "Sent: %s" % sendingData
            self.logger.debug(logString)
            return serialResponse
        except Exception as e:
            self.logger.exception("Error when reading value from device. Data being sent is: %s ", sendingData)
            raise 
    
    def set(self, sendingData):
        try:
            self.logger.debug("Sending data to device. Data:%s" % sendingData)
            self._sendToDevice(self.connection, sendingData)
        except Exception as e:
            self.logger.exception("Error when setting value with data: %s ", sendingData)
            raise 

    def _sendToDevice(self, serialConnection, data):    
        with self.processLock:
            serialConnection.write(data)

    def _readDeviceReponse(self,serialConnection):
        with self.processLock:
            serialResponse = self._readLine(serialConnection)
        return serialResponse

    """
    Custom readline method to avoid end of line char issues
    """
    def _readLine(self, serialConnection):
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

    def clearBuffer(self):
        self.connection.flushInput()

    def deviceOnPort(self, usbPort):
        tempConnection = serial.Serial(usbPort, self.baudRate, timeout = self.timeout)
        self._sendToDevice(tempConnection,self.idMessage)
        deviceResponse = self._readDeviceReponse(tempConnection)
        return self.deviceVerificationFunc(deviceResponse)


    