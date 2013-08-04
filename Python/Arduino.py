import SerialCommunication
import threading
import logging

class ArduinoController():
  def __init__(self, shouldLog = False):
    if shouldLog:
      logging.basicConfig(format='%(asctime)s %(message)s', filename='arduino.log', level=logging.DEBUG)

    self.connection = SerialCommunication.Connection(baudrate = 9600, timeout = 2, handshakeSignal = 7, programId = 17)
    self.processLock = threading.Lock()

    #These values are meant for the device. 'Write' means the device outputs
    self.deviceWriteRealVoltage = 8
    self.deviceWriteRealCurrent = 9
    self.deviceReadTargetVoltage = 10
    self.deviceReadTargetCurrent = 11
    self.deviceWriteTargetVoltage = 12
    self.deviceWriteTargetCurrent = 13
    self.ledStateChange = 14
    self.ledStatus = 0


  def getRealVoltage(self):
    with self.processLock:
      value = self.connection.getValue(self.deviceWriteRealVoltage)
    return value

  def getRealCurrent(self):
    with self.processLock:
      value = self.connection.getValue(self.deviceWriteRealCurrent)
    return value

  def getTargetVoltage(self):
    with self.processLock:
      value = self.connection.getValue(self.deviceWriteTargetVoltage)
    return value

  def getTargetCurrent(self):
    with self.processLock:
      value = self.connection.getValue(self.deviceWriteTargetCurrent)
    return value

  def setTargetVoltage(self, targetVoltage):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetVoltage, int(targetVoltage))

  def setTargetCurrent(self, targetCurrent):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetCurrent, int(targetCurrent))

  def ledSwitch(self):
    with self.processLock:
      if self.ledStatus:
        self.connection.setValue(self.ledStateChange, 0)
        self.ledStatus = 0
      else:
        self.connection.setValue(self.ledStateChange, 1)
        self.ledStatus = 1

  def connect(self):
    with self.processLock:
      connectionSuccessful = self.connection.connect()
    return connectionSuccessful

  def setLogging(self, shouldLog):
    if shouldLog:
      logging.basicConfig(level=logging.DEBUG)
    else:
      logging.propagate = False
