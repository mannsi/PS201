from PsController.Model.Constants import *
from PsController.Utilities.Crc import Crc16

class DeviceValues:
    def __init__(self):
        self.start = 0
        self.command = 0
        self.dataLength = 0
        self.data = ""
        self.crc = [] # list of hex values
        self.serialResponse  = bytearray()

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

    """
    Returns a device responses
    """
    @staticmethod
    def fromSerial(serialValue):
        deviceResponseList = []
        response = DeviceValues()
        response.start = serialValue[0]
        response.command = serialValue[1]
        response.dataLength = serialValue[2]
        index = 3
        response.rawData = serialValue[index:index+response.dataLength]
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
        return response