import logging
from .SerialCommunication import SerialConnection
from .DeviceResponse import DeviceResponse
import PsController.DAL.Constants as dataConstants
from PsController.Model.DeviceValues import DeviceValues

class DataAccess():
    def __init__(self):
        self.connection = SerialConnection(
            baudrate = 9600,
            timeout = 0.1,
            handshakeSignal=dataConstants.deviceWriteRealVoltage,
            startChar=dataConstants.startChar,
            acknowledgeSignal=dataConstants.acknowledgeSignal,
            notAcknowledgeSignal=dataConstants.notAcknowledgeSignal)
        self.deviceRespondCommands = [dataConstants.deviceWriteRealVoltage,
                             dataConstants.deviceWriteRealCurrent,
                             dataConstants.deviceWritePreRegulatorVoltage,
                             dataConstants.deviceWriteTargetVoltage,
                             dataConstants.deviceWriteTargetCurrent,
                             dataConstants.deviceWriteIsOutputOn,
                             dataConstants.deviceWriteInputVoltage
                             ]

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
        serialValues = self.connection.getValue(dataConstants.deviceWriteAll)
        while not serialValues:
            serialValues = self.connection.getValue(dataConstants.deviceWriteAll)
        values = DeviceResponse.fromSerialValue(serialValues, dataConstants.startChar).data
        splitValues = values.split(";") 
        floatValues = [float(value) for value in splitValues]
        return floatValues

    def getRealVoltage(self):
        value = _getValueFromDevice(dataConstants.deviceWriteRealCurrent)
        return float(value)

    def getRealCurrent(self):
        value = _getValueFromDevice(dataConstants.deviceWriteRealVoltage)
        return float(value)

    def getPreRegulatorVoltage(self):
        value = _getValueFromDevice(dataConstants.deviceWritePreRegulatorVoltage)
        return float(value)

    def getTargetVoltage(self):
        value = _getValueFromDevice(dataConstants.deviceWriteTargetVoltage)
        return float(value)

    def getTargetCurrent(self):
        value = _getValueFromDevice(dataConstants.deviceWriteTargetCurrent)
        return float(value)

    def getDeviceIsOn(self):
        value = _getValueFromDevice(dataConstants.deviceWriteIsOutputOn)
        return bool(value)

    def setTargetVoltage(self, targetVoltage):
        self.connection.setValue(dataConstants.deviceReadTargetVoltage, targetVoltage)

    def setTargetCurrent(self, targetCurrent):
        self.connection.setValue(dataConstants.deviceReadTargetCurrent, targetCurrent)
      
    def setOutputOnOff(self, shouldBeOn):
        if shouldBeOn:
            deviceCommand = dataConstants.deviceTurnOnOutput
        else:
            deviceCommand = dataConstants.deviceTurnOffOutput
        self.connection.setValue(deviceCommand)

    def getStreamValues(self):
        serialResponse = self.connection.getValue()
        if not serialResponse: return []
        commandDataList = DeviceResponse.fromSerialStreamValue(serialResponse, dataConstants.startChar)
        commandDataList = self._filterOnlyCommands(commandDataList)
        return commandDataList

    def startStream(self):
        self.connection.setValue(dataConstants.deviceStartStream)

    def _getValueFromDevice(self, command):
        serialValue = self.connection.getValue(command)
        value = DeviceResponse.fromSerialValue(serialValue, dataConstants.startChar).data
        return value

    def _filterOnlyCommands(self, commandDataList):
        return [x for x in commandDataList if x[0] in self.deviceRespondCommands]
  