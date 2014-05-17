from abc import ABCMeta, abstractmethod


class Connection(metaclass=ABCMeta):
    @abstractmethod
    def availableConnections(self):
        pass

    @abstractmethod
    def connect(self, usbPort):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def connected(self):
        pass

    @abstractmethod
    def clearBuffer(self):
        pass

    @abstractmethod
    def deviceOnPort(self, usbPort):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self, sendingData):
        pass