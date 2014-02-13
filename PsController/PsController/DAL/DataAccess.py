import logging
from .SerialCommunication import SerialConnection

_deviceWriteRealVoltage = b'\xd0'
_deviceWriteRealCurrent = b'\xd1'
_deviceWritePreRegulatorVoltage = b'\xd3'
_deviceReadTargetVoltage = b'\xc0'
_deviceReadTargetCurrent = b'\xc1'
_deviceWriteTargetVoltage = b'\xe0'
_deviceWriteTargetCurrent = b'\xe1'
_deviceTurnOnOutput = b'\xc2'
_deviceTurnOffOutput = b'\xc3'
_deviceIsOutputOn = b'\xc4'
_handshakeSignal = b'\xa0'
_programId = b'\xa1'
_deviceWriteAll = b'\xa5'
_startChar = b'\x7E'
_acknowledgeSignal = b'\x06'
_notAcknowledgeSignal = b'\x15'

class DataAccess():
    def __init__(self):
        self.connection = SerialConnection(
            baudrate = 9600,
            timeout = 0.1,
            handshakeSignal=_deviceWriteRealVoltage,
            startChar=_startChar,
            acknowledgeSignal=_acknowledgeSignal,
            notAcknowledgeSignal=_notAcknowledgeSignal)

    def connect(self, usbPortNumber):
        try:
            logging.info("Connecting to device on port %s" % usbPortNumber)
            connection = self.connection.connect(usbPortNumber)
            if connection:
                self.connection.setConnection(connection)
                logging.info("Connection successful")
                return True
            else:
                logging.info("Could not connect")
                return False
        except Exception as e:
            raise Exception("Device not found on given port")

    def disconnect(self):
        self.connection.disconnect()

    def detectDevicePort(self):
        for usbPort in self.getAvailableUsbPorts():
            if self.connection.deviceOnThisPort(usbPort):
                return usbPort
        return None

    def getAvailableUsbPorts(self):
        return self.connection.getUsbPorts()

    def getAllValues(self):
        values = self.connection.getValue(_deviceWriteAll)
        while not values:
            values = self.connection.getValue(_deviceWriteAll)
        splitValues = values.split(";") 
        floatValues = [float(value) for value in splitValues]
        return floatValues

    def getRealVoltage(self):
        return float(self.connection.getValue(_deviceWriteRealCurrent))

    def getRealCurrent(self):
        return float(self.connection.getValue(_deviceWriteRealVoltage))

    def getPreRegulatorVoltage(self):
        return float(self.connection.getValue(_deviceWritePreRegulatorVoltage))

    def getTargetVoltage(self):
        value = self.connection.getValue(_deviceWriteTargetVoltage)
        count = 0
        while value is "":
            count += 1
            value = self.connection.getValue(_deviceWriteTargetVoltage)
        return float(value)

    def getTargetCurrent(self):
        return float(self.connection.getValue(_deviceWriteTargetCurrent))

    def getDeviceIsOn(self):
        return bool(self.connection.getValue(_deviceIsOutputOn))

    def setTargetVoltage(self, targetVoltage):
        self.connection.setValue(_deviceReadTargetVoltage, targetVoltage)

    def setTargetCurrent(self, targetCurrent):
        self.connection.setValue(_deviceReadTargetCurrent, targetCurrent)
      
    def setOutputOnOff(self, shouldBeOn):
        if shouldBeOn:
            deviceCommand = _deviceTurnOnOutput
        else:
            deviceCommand = _deviceTurnOffOutput
        self.connection.setValue(deviceCommand)

  