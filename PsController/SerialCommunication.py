import serial
import sys
import logging
import platform
import glob
import threading
import time
from datetime import datetime
import binascii
import crcmod.predefined

class DeviceResponse:
    def fromSerialValue(self,serialValue, startChar):
        self.idSignal = serialValue[0:1]
        self.aknowledgementSignal = serialValue[1:2]
        self.data = None

        startIndexOfDataRespons = 0
        for x in range(len(serialValue)):
            if serialValue[x:x+1] == startChar and serialValue[x+1:x+2] == startChar: # Check for two startChar in a row. Don't know a better python way to do this
                startIndexOfDataRespons = x + 1 
        
        if startIndexOfDataRespons is not 0:
            dataLength = serialValue[startIndexOfDataRespons + 2]
            if dataLength > 0:
                dataIndex = startIndexOfDataRespons+3
                binaryData = serialValue[dataIndex:dataIndex+dataLength]
                self.data = binaryData.decode()

class Connection():
    def __init__(
                 self, 
                 baudrate, 
                 timeout, 
                 handshakeSignal, 
                 startChar, 
                 acknowledgeSignal, 
                 notAcknowledgeSignal):
        self.baudRate = baudrate
        self.timeout = timeout
        self.handshakeSignal = handshakeSignal
        self.startChar = startChar
        self.acknowledgementSignal = acknowledgeSignal
        self.notAcknowledgeSignal = notAcknowledgeSignal
        self.processLock = threading.Lock()
        
    def setConnection(self, connection):
        self.connection = connection
    
    """
    Get a tuple containing (avilableUsbPorts, defaultUsbPort)
    """
    def getUsbPorts(self):
        defaultPort = None
        system_name = platform.system()
        available = []
        if system_name == "Windows":
            # Scan for available ports.
            for portNumber in range(256):
                try:
                    con = serial.Serial(portNumber, self.baudRate, timeout = 0.01)
                    available.append(con.portstr)
                    if self.validConnection(con):
                        defaultPort = con.portstr
                    con.close()
                except serial.SerialException:
                    pass
        elif system_name == "Darwin":
            # Mac
            usbList = glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
            for usbPort in usbList:
                available.append(usbPort)
        else:
            # Assume Linux or something else
            usbList = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
            for usbPort in usbList:
                available.append(usbPort)
            for port in available:
                try:
                    con = serial.Serial(port, self.baudRate, timeout = 0.01)
                    if self.validConnection(con):
                        defaultPort = con.portstr
                        break
                except serial.SerialException:
                    pass
        return (available, defaultPort)
    
    def validConnection(self, connection):
        try:
            response = self.__sendCommandToDevice__(connection, self.handshakeSignal, '')
            if response.aknowledgementSignal == self.acknowledgementSignal:
                return True
            else:
                return False
        except Exception as e:
            return False 
    
    def deviceOnThisPort(self, usbPortNumber):
        connection = self.connect(usbPortNumber)
        return self.validConnection(connection)
    
    def connect(self, usbPortNumber):
        try:
            connection = serial.Serial(usbPortNumber, self.baudRate, timeout = self.timeout)
            if self.validConnection(connection):
                return connection
            else:
                return None
        except serial.SerialException:
            logging.error("Device not found on given port")
            return False
    
    def disconnect(self):
        self.connection.close()
    
    def getValue(self, command):
        logging.debug("Sending command to device. Command: %s" % command)
        try:
            value = self.__getValue__(self.connection,command)
            logging.debug("Reading message from device. Value: %s" % value)
            return value
        except Exception as e:
            self.disconnect()
            logging.exception("Error when reading value with command: ", command)
            raise 
    
    def __getValue__(self, serialConnection, command):
        with self.processLock:
            response = self.__sendCommandToDevice__(serialConnection, command,'')   
        return response.data
    
    def setValue(self, command, value = None):
      try:
          loggingString = "Sending command to device. Command:%s" % command
          if value:
              loggingString += ". value:%s" % value
          logging.debug(loggingString)
          self.__setValue__(self.connection, command, value)
      except Exception as e:
          self.disconnect()
          logging.exception("Error when setting value with command: ", command, " and value: ", value)
          raise 
    
    def __setValue__(self, serialConnection, command, value): 
        with self.processLock:
            self.__sendCommandToDevice__(serialConnection, command, value)

    def __sendCommandToDevice__(self, serialConnection, command, data):
        binaryData = bytes(str(data), 'ascii')
        dataLength = bytes([len(binaryData)])
        crc = CreateCRC16Code(command, binaryData)
        serialConnection.write(self.startChar)
        serialConnection.write(command)
        serialConnection.write(dataLength)
        if len(binaryData) > 0:
            serialConnection.write(binaryData)
        serialConnection.write(crc[0])
        serialConnection.write(self.startChar)
    
        response = self.__readDeviceReponse__(serialConnection)
        if response.idSignal == self.startChar:
            return response

        raise Exception("Got neither an ACK nor NAK from device")

    def __readDeviceReponse__(self,serialConnection):
        serialResponse = serialConnection.readline()
        response = DeviceResponse()
        response.fromSerialValue(serialResponse, self.startChar)
        return response

    
def CreateCRC16Code(command, binaryData):
    crc16 = crcmod.predefined.Crc('xmodem')
    crc16.update(command) #command
    crc16.update(bytes([len(binaryData)])) #length
    crc16.update(binaryData)
    hexCode = hex(crc16.crcValue)
    hexArray = (crc16.crcValue).to_bytes(2, byteorder='big')
    return (hexArray, hexCode)

