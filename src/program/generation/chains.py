from abc import ABC, abstractmethod

from models import PromptInput


class IChain(ABC):
    @abstractmethod
    def generate_commit_message(self, prompt_input: PromptInput) -> str:
        pass
