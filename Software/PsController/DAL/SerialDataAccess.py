from PsController.DAL.SerialMapping import SerialMapping


class SerialDataAccess():
    @staticmethod
    def sendValueToDevice(connection, command, data=''):
        bytesToSend = SerialMapping.toSerial(command, data)
        connection.set(bytesToSend)

    @staticmethod
    def getResponseFromDevice(connection):
        serialValue = connection.get()
        if not serialValue:
            return None
        return SerialMapping.fromSerial(serialValue)