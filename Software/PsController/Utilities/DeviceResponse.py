from PsController.Model.Constants import *
from PsController.Utilities.Crc import Crc16


class DeviceResponse:
    def __init__(self):
        self.start = 0
        self.command = 0
        self.dataLength = 0
        self.data = ""
        self.crc = []  # list of int values
        self.serialResponse = bytearray()
        self.readableSerial = []


class DeviceCommunication:
    @classmethod
    def toSerial(cls, command, data):
        binaryData = bytes(str(data), 'ascii')
        crcCode = Crc16.create(command, binaryData)
        dataLength = len(binaryData)

        byteArray = bytearray()
        byteArray.append(START)
        byteArray.append(command)
        byteArray.append(dataLength)
        if dataLength > 0:
            for intData in binaryData:
                byteArray.append(intData)
        for crc in crcCode:
            byteArray.append(crc)
        byteArray.append(START)
        return byteArray

    @classmethod
    def toReadableSerial(cls, command, data):
        serialValue = cls.toSerial(command, data)
        response = cls.fromSerial(serialValue)
        return response.readableSerial

    @classmethod
    def fromSerial(cls, serialValue):
        """Converts a bytes object into a device response object"""
        response = DeviceResponse()
        try:
            response.start = serialValue[0]
            response.command = serialValue[1]
            response.dataLength = serialValue[2]
            index = 3
            response.rawData = serialValue[index:index + response.dataLength]
            response.data = response.rawData.decode()
            index += response.dataLength
            response.crc = []
            while True:
                value = serialValue[index]
                if value == START:
                    break
                response.crc.append(value)
                index += 1
                if index >= len(serialValue):
                    raise Exception("End char missing. Received %s" % serialValue)
            response.end = serialValue[index]
            response.serialResponse = serialValue
            cls._setReadableSerialValue(response)
        except Exception as e:
            raise SerialException(e.args[0])
        return response

    @classmethod
    def _setReadableSerialValue(cls, response):
        response.readableSerial.append(cls._printableHex(response.start))
        response.readableSerial.append(cls._printableHex(response.command))
        response.readableSerial.append(cls._printableHex(response.dataLength))
        if response.rawData:
            response.readableSerial.append(response.rawData.decode("utf-8"))
        for crc in response.crc:
            response.readableSerial.append(cls._printableHex(crc))
        response.readableSerial.append(cls._printableHex(response.end))

    @staticmethod
    def _printableHex(intValue):
        hexString = format(intValue, 'x')
        if len(hexString) == 1:
            hexString = '0' + hexString
        return hexString


class SerialException(Exception):
    pass