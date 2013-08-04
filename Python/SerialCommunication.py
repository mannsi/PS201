import serial
import sys
import logging

class Connection():
  def __init__(self, baudrate, timeout, handshakeSignal, programId):
    self.portFound = False
    self.baudRate = baudrate
    self.timeout = timeout
    self.portNumber = -1
    self.programId = programId
    self.connected = False
    self.handshakeSignal = handshakeSignal

  def __findArduinoPort__(self):
    for portNumber in range(256):
      try:
        connection = serial.Serial(portNumber, self.baudRate, timeout = self.timeout)
        logging.info("Checking for Arduino on port %s" % portNumber)
        correctPort = self.__arduinoOnThisPort__(portNumber, connection)
        if correctPort:
          return (portNumber, connection)
        connection.close()
      except serial.SerialException:
          pass
    raise Exception("No device found on any port")

  def __arduinoOnThisPort__(self, portNumber, connection):
    while True:
        try:
          readValue = int(connection.read())
          if readValue:
            if readValue == self.handshakeSignal:
              return True
            else:
              return False
          else:
            return False
        except:
          return False

  def connect(self):
    if not self.connected:
      try:
        (portNumber, connection) = self.__findArduinoPort__()
        self.connection = connection
        self.connected = True
        logging.info("Connected")
        return True
      except Exception as err:
        logging.info("Error connecting to port. Error message: %s" % err)
        return False
    return True

  def disconnect(self):
    self.connection.close()

  def getValue(self, command):
    self.connect()
    value = self.__getValue__(self.connection,command)
    return value

  def __getValue__(self, serialConnection, command):
    stream = bytearray(3)
    stream[0] = self.programId
    stream[1] = command
    stream[2] = 0
    logging.debug("Sending command to arduino. Command: %s" % command)
    serialConnection.write(stream)
    logging.info("Reading message from arduino")
    value = int(serialConnection.read())
    logging.debug("Value from arduino: %s" % value)
    return value

  def setValue(self, command, value):
    self.connect()
    self.__setValue__(self.connection, command, value)

  def __setValue__(self, serialConnection, command, value):
    stream = bytearray(3)
    stream[0] = self.programId
    stream[1] = command
    stream[2] = value
    logging.debug("Sending command to arduino. Command:%s" % command, ". value:%s" % value)
    serialConnection.write(stream)