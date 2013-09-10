import serial
import sys
import logging
import platform
import glob

class Connection():
  def __init__(self, baudrate, timeout, handshakeSignal, programId):
    self.portFound = False
    self.baudRate = baudrate
    self.timeout = timeout
    self.programId = programId
    self.handshakeSignal = handshakeSignal
    self.connected = False

  def __connectToDevice__(self):
    if self.portNumber is not None:
      try:
        logging.info("Connecting to device on port %s" % self.portNumber)
        connection = serial.Serial(self.portNumber, self.baudRate, timeout = self.timeout)
        correctPort = self.__deviceOnThisPort__(self.portNumber, connection)
        if correctPort:
          return (self.portNumber, connection)
        else:
          raise Exception("Device did not respond")
      except serial.SerialException:
        raise Exception("Device not found on given port")
    else:
      print("Port not given")
      for portNumber in range(256):
        try:
          connection = serial.Serial(portNumber, self.baudRate, timeout = self.timeout)
          logging.info("Checking for device on port %s" % portNumber)
          correctPort = self.__deviceOnThisPort__(portNumber, connection)
          if correctPort:
            return (portNumber, connection)
          connection.close()
        except serial.SerialException:
            pass
      raise Exception("No device found on any port")

  def __deviceOnThisPort__(self, portNumber, connection):
    while True:
        try:
          connection.write(self.handshakeSignal)
          readValue = connection.readline()
          if readValue:
            if readValue == self.programId:
              return True
            else:
              return False
          else:
            return False
        except:
          return False

  def getAvailableUsbPorts(self):
    system_name = platform.system()
    if system_name == "Windows":
      # Scan for available ports.
      available = dict()
      for portNumber in range(256):
        try:
          con = serial.Serial(portNumber, self.baudRate, timeout = self.timeout)
          available[con.portstr] = portNumber
          con.close()
        except serial.SerialException:
          pass
      return available
    elif system_name == "Darwin":
      # Mac
      return [(x,x) for x in glob.glob('/dev/tty*') + glob.glob('/dev/cu*')]
    else:
      # Assume Linux or something else
      return [(x,x) for x in glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')]

  def connect(self, usbPortNumber):
    if not self.connected:
      try:
        self.portNumber = usbPortNumber
        logging.info("Trying to connect")
        (portNumber, connection) = self.__connectToDevice__()
        self.connection = connection
        self.connected = True
        logging.info("Connected on port number %s" % usbPortNumber)
        return True
      except Exception as e:
        logging.info("Error connecting to port. Error message: %s" % e)
        return False
    return True

  def disconnect(self):
    self.connection.close()

  def getValue(self, command):
    try:
      value = self.__getValue__(self.connection,command)
      return value
    except Exception as e:
      self.connection.close()
      self.connected = False
      raise Exception()

  def __getValue__(self, serialConnection, command):
    logging.debug("Sending command to arduino. Command: %s" % command)
    serialConnection.write(command)
    value = serialConnection.readline()
    returnValue = str(value, 'ascii').strip()
    logging.debug("Reading message from arduino. Value: %s" % returnValue)
    return returnValue

  def setValue(self, command, value = None):
    try:
      self.__setValue__(self.connection, command, value)
    except Exception as e:
      self.connection.close()
      self.connected = False
      raise Exception()

  def __setValue__(self, serialConnection, command, value):
    loggingString = "Sending command to arduino. Command:%s" % command
    if value:
      loggingString += ". value:%s" % value
    logging.debug(loggingString)
    serialConnection.write(command)
    if value:
      serialConnection.write(value)