from PsController.Utilities.DeviceResponse import DeviceCommunication

class DataAccess():
    def __init__(self, connection, logger):
        self.connection = connection
        self.logger = logger

    def sendValueToDevice(self, command, data=''):
        bytesToSend = DeviceCommunication.toSerial(command, data)
        self.connection.set(bytesToSend)

    def getResponseFromDevice(self):
        serialValue = self.connection.get()
        if not serialValue: return None
        return DeviceCommunication.fromSerial(serialValue)

