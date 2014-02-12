import serial
import crcmod.predefined
import struct
import time
import binascii

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

startChar = b'\x7E'
acknowledgeSignal = b'\x06'
notAcknowledgeSignal = b'\x15'

class DeviceResponse:
    def fromSerialValue(self,serialValue):
        self.idSignal = serialValue[0:1]
        self.aknowledgementSignal = serialValue[1:2]

        startIndexOfDataRespons = 0
        for x in range(len(serialValue)):
            if serialValue[x:x+1] == startChar and serialValue[x+1:x+2] == startChar: # Check for two startChar in a row. Don't know a better python way to do this
                startIndexOfDataRespons = x + 1 
        
        if startIndexOfDataRespons is not 0:
            dataLength = serialValue[startIndexOfDataRespons + 2]
            if dataLength > 0:
                dataIndex = startIndexOfDataRespons+3
                binaryData = serialValue[dataIndex:dataIndex+dataLength]
                self.data = binaryData.decode()

def CreateCRC16Code(command, binaryData):
    crc16 = crcmod.predefined.Crc('xmodem')
    crc16.update(command) #command
    crc16.update(bytes([len(binaryData)])) #length
    crc16.update(binaryData)
    hexCode = hex(crc16.crcValue)
    hexArray = (crc16.crcValue).to_bytes(2, byteorder='big')
    return (hexArray, hexCode)

def ReadDeviceReponse(serialConnection):
    serialResponse = serialConnection.readline()
    response = DeviceResponse()
    response.fromSerialValue(serialResponse)
    return response


con = serial.Serial('COM4', 9600, timeout=1)
#response = SendCommandToDevice(con, __deviceReadTargetVoltage__, 5)
#print("Data response: " , response.data)
#response = SendCommandToDevice(con, __deviceWriteRealVoltage__, '')
#print("Data response: " , response.data)
response = SendCommandToDevice(con, __deviceWriteAll__, '')
print("Data response: " , response.data)