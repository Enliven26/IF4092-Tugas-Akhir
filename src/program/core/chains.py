from abc import ABC, abstractmethod

from core.models import CommitMessageGenerationPromptInputModel


class ICommitMessageGenerationChain(ABC):
    @abstractmethod
    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> str:
        pass


class IDataGenerationChain(ABC):
    @abstractmethod
    def generate_high_level_context(self, diff: str) -> str:
        pass
