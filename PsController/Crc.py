import serial
import sys
import logging
import platform
import glob
import threading
import time
from datetime import datetime
import binascii
import crcmod.predefined

class Crc16:
    @classmethod
    def Create(cls, command, binaryData):
        crc16 = crcmod.predefined.Crc('xmodem')
        crc16.update(command) #command
        crc16.update(bytes([len(binaryData)])) #length
        crc16.update(binaryData)
        hexCode = hex(crc16.crcValue)
        hexArray = (crc16.crcValue).to_bytes(2, byteorder='big')
        return (hexArray, hexCode)

