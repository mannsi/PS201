import serial
import sys
import logging
import platform
import glob
import threading
from datetime import datetime

class Connection():
    def __init__(self, baudrate, timeout, handshakeSignal, programId):
        self.baudRate = baudrate
        self.timeout = timeout
        self.programId = programId
        self.handshakeSignal = handshakeSignal
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
            try:
                for port in available:
                    con = serial.Serial(port, self.baudRate, timeout = 0.01)
                    if self.validConnection(con):
                        defaultPort = con.portstr
                        break
            except serial.SerialException:
                    pass
        return (available, defaultPort)
    
    def validConnection(self, connection):
        try:
            readValue = self.__getValue__(connection, self.handshakeSignal).strip()
            if readValue:
                if readValue == self.programId:
                  return True
                else:
                  return False
            else:
                return False
        except:
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
            value = str(self.__getValue__(self.connection,command), 'ascii').strip()
            logging.debug("Reading message from device. Value: %s" % value)
            return value
        except Exception as e:
            self.disconnect()
            logging.error("ERROR when getting command ", command, " from device")
            raise Exception()
    
    def __getValue__(self, serialConnection, command):
        with self.processLock:
            serialConnection.write(command)
            value = serialConnection.readline()   
        return value
    
    def setValue(self, command, value = None):
      try:
          loggingString = "Sending command to device. Command:%s" % command
          if value:
              loggingString += ". value:%s" % value
          logging.debug(loggingString)
          self.__setValue__(self.connection, command, value)
      except Exception as e:
          self.disconnect()
          logging.error("ERROR when sending command ", command , " to device with value ", value )
          raise Exception()
    
    def __setValue__(self, serialConnection, command, value): 
        with self.processLock:
            serialConnection.write(command)
            if value is not None:
                serialConnection.write(value)
