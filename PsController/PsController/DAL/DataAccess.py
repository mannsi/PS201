import logging
from .SerialCommunication import SerialConnection

__deviceWriteRealVoltage__ = b'\xd0'
__deviceWriteRealCurrent__ = b'\xd1'
__deviceWritePreRegulatorVoltage__ = b'\xd3'
__deviceReadTargetVoltage__ = b'\xc0'
__deviceReadTargetCurrent__ = b'\xc1'
__deviceWriteTargetVoltage__ = b'\xe0'
__deviceWriteTargetCurrent__ = b'\xe1'
__deviceTurnOnOutput__ = b'\xc2'
__deviceTurnOffOutput__ = b'\xc3'
__deviceIsOutputOn__ = b'\xc4'
__handshakeSignal__ = b'\xa0'
__programId__ = b'\xa1'
__deviceWriteAll__ = b'\xa5'
__startChar__ = b'\x7E'
__acknowledgeSignal__ = b'\x06'
__notAcknowledgeSignal__ = b'\x15'

class DataAccess():
    def __init__(self):
        self.connection = SerialConnection(
            baudrate = 9600,
            timeout = 0.1,
            handshakeSignal=__deviceWriteRealVoltage__,
            startChar=__startChar__,
            acknowledgeSignal=__acknowledgeSignal__,
            notAcknowledgeSignal=__notAcknowledgeSignal__)

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
        values = self.connection.getValue(__deviceWriteAll__)
        while not values:
            values = self.connection.getValue(__deviceWriteAll__)
        splitValues = values.split(";") 
        floatValues = [float(value) for value in splitValues]
        return floatValues

    def getRealVoltage(self):
        return float(self.connection.getValue(__deviceWriteRealCurrent__))

    def getRealCurrent(self):
        return float(self.connection.getValue(__deviceWriteRealVoltage__))

    def getPreRegulatorVoltage(self):
        return float(self.connection.getValue(__deviceWritePreRegulatorVoltage__))

    def getTargetVoltage(self):
        value = self.connection.getValue(__deviceWriteTargetVoltage__)
        count = 0
        while value is "":
            count += 1
            value = self.connection.getValue(__deviceWriteTargetVoltage__)
        return float(value)

    def getTargetCurrent(self):
        return float(self.connection.getValue(__deviceWriteTargetCurrent__))

    def getDeviceIsOn(self):
        return bool(self.connection.getValue(__deviceIsOutputOn__))

    def setTargetVoltage(self, targetVoltage):
        self.connection.setValue(__deviceReadTargetVoltage__, targetVoltage)

    def setTargetCurrent(self, targetCurrent):
        self.connection.setValue(__deviceReadTargetCurrent__, targetCurrent)
      
    def setOutputOnOff(self, shouldBeOn):
        if shouldBeOn:
            deviceCommand = __deviceTurnOnOutput__
        else:
            deviceCommand = __deviceTurnOffOutput__
        self.connection.setValue(deviceCommand)

  