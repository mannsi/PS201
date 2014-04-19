class DeviceResponse:
    def __init__(self):
        self.start = 0
        self.command = 0
        self.dataLength = 0
        self.data = ""
        self.crc = []  # list of int values
        self.serialResponse = bytearray()
        self.readableSerial = []