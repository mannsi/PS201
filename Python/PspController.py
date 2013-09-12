import SerialCommunication
import threading
import logging
import struct

class Controller():
  def __init__(self, shouldLog = False, loglevel = logging.ERROR):
    if shouldLog:
      logging.basicConfig(format='%(asctime)s %(message)s', filename='PSP200.log', level=loglevel)

    self.connection = SerialCommunication.Connection(baudrate = 9600, timeout = 2, handshakeSignal = b'\xa0', programId = b'\xa1')
    self.processLock = threading.Lock()

    #These values are meant for the device. 'Write' means the device outputs
    self.deviceWriteRealVoltage = b'\xd0'
    self.deviceWriteRealCurrent = b'\xd1'
    self.deviceWritePreRegulatorVoltage = b'\xd3'
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
      value = float(self.connection.getValue(self.deviceWriteRealVoltage))
    return value

  def getRealCurrent(self):
    with self.processLock:
      value = float(self.connection.getValue(self.deviceWriteRealCurrent)) * 1000
    return value

  def getPreRegulatorVoltage(self):
    with self.processLock:
      value = float(self.connection.getValue(self.deviceWritePreRegulatorVoltage))
    return value

  def getTargetVoltage(self):
    with self.processLock:
      value = self.connection.getValue(self.deviceWriteTargetVoltage)
    return value

  def getTargetCurrent(self):
    with self.processLock:
      value = float(self.connection.getValue(self.deviceWriteTargetCurrent)) * 1000
    return value

  # TODO
  def getOutputOnOff(self):
    with self.processLock:
      value = True
      #value = self.connection.getValue(self.deviceWriteTargetCurrent)
    return value

  def setTargetVoltage(self, targetVoltage):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetVoltage, struct.pack(">H",int(100*targetVoltage)))

  def setTargetCurrent(self, targetCurrent):
    with self.processLock:
      self.connection.setValue(self.deviceReadTargetCurrent, struct.pack(">H",int(targetCurrent/10)))

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
