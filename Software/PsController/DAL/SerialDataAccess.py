from PsController.Utilities.DeviceResponse import DeviceCommunication

class DataAccess():
    @staticmethod
    def sendValueToDevice(self, connection, command, data=''):
        bytesToSend = DeviceCommunication.toSerial(command, data)
        connection.set(bytesToSend)

    @staticmethod
    def getResponseFromDevice(self, connection):
        serialValue = self.connection.get()
        if not serialValue: return None
        return DeviceCommunication.fromSerial(serialValue)

