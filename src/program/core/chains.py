from abc import ABC, abstractmethod

from core.constants import DATA_GENERATION_PROMPT_TEMPLATE
from core.models import CommitMessageGenerationPromptInputModel
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


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


class DataGenerationChain(IDataGenerationChain):
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__()

        prompt = PromptTemplate.from_template(DATA_GENERATION_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    def generate_high_level_context(self, diff: str) -> str:
        return self.__chain.invoke({"diff": diff})
