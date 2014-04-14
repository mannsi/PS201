import crcmod.predefined

from PsController.Model.Settings import *


class Crc16:
    @classmethod
    def create(cls, command, binaryData):
        bytesCommand = bytes([command])
        crc16 = crcmod.predefined.Crc('xmodem')
        crc16.update(bytesCommand)
        crc16.update(bytes([len(binaryData)]))
        crc16.update(binaryData)
        unescapedHexCrc = cls._getHexListFromInt(crc16.crcValue)
        escapedIntCrcCode = cls._escapeCrcCode(unescapedHexCrc, charactersToEscape)
        return escapedIntCrcCode

    @staticmethod
    def _escapeCrcCode(unescapedCrcCode, valuesToEscape):
        crcCode = []
        for unescapedCrcByte in unescapedCrcCode:
            intCrcValue = int(unescapedCrcByte, 16)
            if intCrcValue in valuesToEscape:
                crcCode.append(ESCAPE)
                crcCode.append(FLIP ^ intCrcValue)
            else:
                crcCode.append(intCrcValue)
        return crcCode

    @staticmethod
    def _getHexListFromInt(intValue):
        """Splits a 4 char hex code into 2x 2 char hex code i.e 0x1234 becomes [0x12, 0x34]"""
        return [hex(x) for x in divmod(intValue, 0x100)]