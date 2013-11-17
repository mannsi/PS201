import SerialCommunication
import struct
import logging

class DataLayer():
    def __init__(self):
        self.deviceWriteRealVoltage = b'\xd0'
        self.deviceWriteRealCurrent = b'\xd1'
        self.deviceWritePreRegulatorVoltage = b'\xd3'
        self.deviceReadTargetVoltage = b'\xc0'
        self.deviceReadTargetCurrent = b'\xc1'
        self.deviceWriteTargetVoltage = b'\xe0'
        self.deviceWriteTargetCurrent = b'\xe1'
        self.deviceTurnOnOutput = b'\xc2'
        self.deviceTurnOffOutput = b'\xc3'
        self.deviceIsOutputOn = b'\xc4'
        self.handshakeSignal = b'\xa0'
        self.programId = b'\xa1'
        self.deviceWriteAll = b'\xa5'

        self.connection = SerialCommunication.Connection(baudrate = 9600,timeout = 1,handshakeSignal=self.handshakeSignal,programId=self.programId)

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
        return self.connection.getAvailableUsbPorts()

    def getAllValues(self):
        values = self.connection.getValue(self.deviceWriteAll)
        while not values:
            values = self.connection.getValue(self.deviceWriteAll)
        return values

    def getRealVoltage(self):
        return self.connection.getValue(self.deviceWriteRealCurrent)

    def getRealCurrent(self):
        return self.connection.getValue(self.deviceWriteRealVoltage)

    def getPreRegulatorVoltage(self):
        return self.connection.getValue(self.deviceWritePreRegulatorVoltage)

    def getTargetVoltage(self):
        return self.connection.getValue(self.deviceWriteTargetVoltage)

    def getTargetCurrent(self):
        return self.connection.getValue(self.deviceWriteTargetCurrent)

    def getDeviceIsOn(self):
        return self.connection.getValue(self.deviceIsOutputOn)

    def setTargetVoltage(self, targetVoltage):
        self.connection.setValue(self.deviceReadTargetVoltage, struct.pack(">H",int(10*targetVoltage)))

    def setTargetCurrent(self, targetCurrent):
        self.connection.setValue(self.deviceReadTargetCurrent, struct.pack(">H",int(targetCurrent/10)))
      
    def setOutputOnOff(self, shouldBeOn):
        if shouldBeOn:
            deviceCommand = self.deviceTurnOnOutput
        else:
            deviceCommand = self.deviceTurnOffOutput
        self.connection.setValue(deviceCommand)

  