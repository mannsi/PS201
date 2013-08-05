import serial
import sys
import logging

class Connection():
  def __init__(self, baudrate, timeout, handshakeSignal, programId):
    self.portFound = False
    self.baudRate = baudrate
    self.timeout = timeout
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
        print("Trying to connect")
        (portNumber, connection) = self.__findArduinoPort__()
        print("Connecion success")
        self.connection = connection
        self.connected = True
        logging.info("Connected on port %s" % portNumber)
        return True
      except Exception as e:
        logging.info("Error connecting to port. Error message: %s" % e)
        return False
    return True

  def disconnect(self):
    self.connection.close()

  def getValue(self, command):
    self.connect()
    try:
      value = self.__getValue__(self.connection,command)
      return value
    except Exception as e:
      self.connection.close()
      self.connected = False
      raise Exception()

  def __getValue__(self, serialConnection, command):
    stream = bytearray(3)
    stream[0] = self.programId
    stream[1] = command
    stream[2] = 0
    logging.debug("Sending command to arduino. Command: %s" % command)
    serialConnection.write(stream)
    value = int(serialConnection.read())
    logging.debug("Reading message from arduino. Value: %s" % value)
    return value

  def setValue(self, command, value):
    self.connect()
    try:
      self.__setValue__(self.connection, command, value)
    except Exception as e:
      self.connection.close()
      self.connected = False
      raise Exception()

  def __setValue__(self, serialConnection, command, value):
    stream = bytearray(3)
    stream[0] = self.programId
    stream[1] = command
    stream[2] = value
    logging.debug("Sending command to arduino. Command:%s" % command, ". value:%s" % value)
    serialConnection.write(stream)