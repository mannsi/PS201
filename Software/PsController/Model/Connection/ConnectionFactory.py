from abc import ABCMeta, abstractmethod


class ConnectionFactory(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, logger):
        self.connection = None
        self.logger = logger

    @abstractmethod
    def getConnection(self):
        """
        Returns a Connection object
        """
        pass
