from .SerialConnection import SerialConnection
from ..DataMapping.SerialDataMapping import SerialDataMapping
from ..Constants import *


class SerialConnectionFactory:
    def __init__(self, logger):
        self.connection = None
        self.logger = logger

    def getConnection(self):
        if self.connection:
            return self.connection
        else:
            self.connection = SerialConnection(
                baudRate=9600,
                timeout=0.1,
                logger=self.logger,
                idMessage=SerialConnectionFactory._getDeviceIdMessage(),
                deviceVerificationFunc=self._deviceIdResponseFunction)
            return self.connection

    @staticmethod
    def _getDeviceIdMessage():
        """Gives the messages needed to send to device to verify that device is using a given port"""
        return SerialDataMapping.toSerial(HANDSHAKE, data='')

    def _deviceIdResponseFunction(self, serialResponse):
        """Function used to verify an id response from device, i.e. if the response come from our device or not"""
        try:
            if not serialResponse:
                self.logger.info("Did not receive an ACKNOWLEDGE response")
                return False
            response = SerialDataMapping.fromSerial(serialResponse)
            return response.command == ACKNOWLEDGE
        except:
            self.logger.info("Did not receive an ACKNOWLEDGE response")
            return False