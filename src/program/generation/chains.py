from abc import ABC, abstractmethod

class IChain(ABC):
    @abstractmethod
    def generate_commit_message(self, diff: str) -> str:
        # TODO: design the interface so that it can also accept additional data (commit hash, etc)
        pass