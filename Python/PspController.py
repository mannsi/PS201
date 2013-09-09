import SerialCommunication
import threading
import logging

class Controller():
  def __init__(self, loglevel = logging.ERROR):
    logging.basicConfig(format='%(asctime)s %(message)s', filename='PSP200.log', level=loglevel)

    self.connection = SerialCommunication.Connection(baudrate = 9600, timeout = 2, handshakeSignal = b'\xa0', programId = b'\xa1')
    self.processLock = threading.Lock()

    #These values are meant for the device. 'Write' means the device outputs
    self.deviceWriteRealVoltage = b'\xd0'
    self.deviceWriteRealCurrent = b'\xd1'
    self.deviceReadTargetVoltage = b'\xc0'
    self.deviceReadTargetCurrent = b'\xc1'
    self.deviceWriteTargetVoltage = b'\xe0'
    self.deviceWriteTargetCurrent = b'\xe1'
    self.deviceTurnOnOutput = b'\xc2'
    self.deviceTurnOffOutput = b'\xc3'

  def connect(self, usbPortNumber):
    with self.processLock:
      connectionSuccessful = self.connection.connect(usbPortNumber)
    return connectionSuccessful

  def getAvailableUsbPorts(self):
    return self.connection.getAvailableUsbPorts()

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

  # TODO
  def getOutputOnOff(self):
    with self.processLock:
      value = True
      #value = self.connection.getValue(self.deviceWriteTargetCurrent)
    return value

  def setTargetVoltage(self, targetVoltage):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetVoltage, targetVoltage)

  def setTargetCurrent(self, targetCurrent):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetCurrent, targetCurrent)

  def setOutputOnOff(self, shouldBeOn):
    if shouldBeOn:
      deviceCommand = self.deviceTurnOnOutput
    else:
      deviceCommand = self.deviceTurnOffOutput
    with self.processLock:
      self.connection.setValue(deviceCommand)

  def setLogging(self, shouldLog, loglevel):
    if shouldLog:
      logging.basicConfig(level=loglevel)
    else:
      logging.propagate = False
