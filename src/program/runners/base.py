from abc import ABC, abstractmethod

class IProgramRunner(ABC):
    @abstractmethod
    def run(self):
        pass