
from abc import ABC, abstractmethod

class Frontier(ABC):

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def add(self, step):
        pass


