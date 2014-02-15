
class DeviceResponse:
    def fromSerialValue(self,serialValue, startChar):
        self.idSignal = serialValue[0:1]
        self.aknowledgementSignal = serialValue[1:2]
        self.data = None

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