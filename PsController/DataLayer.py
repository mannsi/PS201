import SerialCommunication
import logging

class DataLayer():
    def __init__(self):
        self.__deviceWriteRealVoltage__ = b'\xd0'
        self.__deviceWriteRealCurrent__ = b'\xd1'
        self.__deviceWritePreRegulatorVoltage__ = b'\xd3'
        self.__deviceReadTargetVoltage__ = b'\xc0'
        self.__deviceReadTargetCurrent__ = b'\xc1'
        self.__deviceWriteTargetVoltage__ = b'\xe0'
        self.__deviceWriteTargetCurrent__ = b'\xe1'
        self.__deviceTurnOnOutput__ = b'\xc2'
        self.__deviceTurnOffOutput__ = b'\xc3'
        self.__deviceIsOutputOn__ = b'\xc4'
        self.__handshakeSignal__ = b'\xa0'
        self.__programId__ = b'\xa1'
        self.__deviceWriteAll__ = b'\xa5'
        self.__startChar__ = b'\x7E'
        self.__acknowledgeSignal__ = b'\x06'
        self.__notAcknowledgeSignal__ = b'\x15'

        self.connection = SerialCommunication.Connection(
                                                         baudrate = 9600,
                                                         timeout = 0.1,
                                                         handshakeSignal=self.__deviceWriteRealVoltage__,
                                                         startChar=self.__startChar__,
                                                         acknowledgeSignal=self.__acknowledgeSignal__,
                                                         notAcknowledgeSignal=self.__notAcknowledgeSignal__)

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
        values = self.connection.getValue(self.__deviceWriteAll__)
        while not values:
            values = self.connection.getValue(self.__deviceWriteAll__)
        splitValues = values.split(";") 
        floatValues = [float(value) for value in splitValues]
        return floatValues

    def getRealVoltage(self):
        return float(self.connection.getValue(self.__deviceWriteRealCurrent__))

    def getRealCurrent(self):
        return float(self.connection.getValue(self.__deviceWriteRealVoltage__))

    def getPreRegulatorVoltage(self):
        return float(self.connection.getValue(self.__deviceWritePreRegulatorVoltage__))

    def getTargetVoltage(self):
        value = self.connection.getValue(self.__deviceWriteTargetVoltage__)
        count = 0
        while value is "":
            count += 1
            value = self.connection.getValue(self.__deviceWriteTargetVoltage__)
        return float(value)

    def getTargetCurrent(self):
        return float(self.connection.getValue(self.__deviceWriteTargetCurrent__))

    def getDeviceIsOn(self):
        return bool(self.connection.getValue(self.__deviceIsOutputOn__))

    def setTargetVoltage(self, targetVoltage):
        self.connection.setValue(self.__deviceReadTargetVoltage__, targetVoltage)

    def setTargetCurrent(self, targetCurrent):
        self.connection.setValue(self.__deviceReadTargetCurrent__, targetCurrent)
      
    def setOutputOnOff(self, shouldBeOn):
        if shouldBeOn:
            deviceCommand = self.__deviceTurnOnOutput__
        else:
            deviceCommand = self.__deviceTurnOffOutput__
        self.connection.setValue(deviceCommand)

  