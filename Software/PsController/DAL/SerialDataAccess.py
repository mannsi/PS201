from PsController.Utilities.DeviceResponse import DeviceCommunication

class DataAccess():
    @staticmethod
    def sendValueToDevice(connection, command, data=''):
        bytesToSend = DeviceCommunication.toSerial(command, data)
        connection.set(bytesToSend)

    @staticmethod
    def getResponseFromDevice(connection):
        serialValue = connection.get()
        if not serialValue: return None
        return DeviceCommunication.fromSerial(serialValue)

