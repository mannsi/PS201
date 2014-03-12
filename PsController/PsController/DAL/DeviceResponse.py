class DeviceResponse:
    @staticmethod
    def fromSerialValue(serialValue, startChar):
        response = DeviceResponse()
        response.idSignal = serialValue[0:1]
        response.aknowledgementSignal = serialValue[1:2]
        response.data = None

        startIndexOfDataRespons = 0
        for x in range(len(serialValue)):
            if serialValue[x:x+1] == startChar and serialValue[x+1:x+2] == startChar: # Check for two startChar in a row. Don't know a better python way to do this
                startIndexOfDataRespons = x + 1 
        
        if startIndexOfDataRespons is not 0:
            dataLength = serialValue[startIndexOfDataRespons + 2]
            if dataLength > 0:
                dataIndex = startIndexOfDataRespons+3
                binaryData = serialValue[dataIndex:dataIndex+dataLength]
                response.data = binaryData.decode()
        return response

    """
    Returns a list of tuples (command, data)
    """
    @staticmethod
    def fromSerialStreamValue(serialValue, startChar):
        commandDataList = []
        while serialValue:
            start = serialValue[0:1]
            command = serialValue[1:2]
            dataLength = serialValue[2]
            data = serialValue[3:3+dataLength]
            crc = serialValue[3+dataLength:5+dataLength]
            end = serialValue[5+dataLength:6+dataLength]
            totalLength = 6+dataLength
            serialValue = serialValue[totalLength:]
            commandDataList.append((command, data))
        return commandDataList
        