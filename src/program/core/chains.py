import os
import random
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langsmith import traceable

from core.constants import (
    DATA_GENERATION_PROMPT_TEMPLATE,
    DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE,
    HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    RANDOM_REQUIREMENT_ID_FORMATS,
    END_DOCUMENT_SPLIT_SEPARATOR
)
from core.models import (
    CommitMessageGenerationPromptInputModel,
    DataGenerationPromptInputModel,
)

TRunnableInput = TypeVar("TRunnableInput")
TRunnableOutput = TypeVar("TRunnableOutput")


class BaseRunnable(Generic[TRunnableInput, TRunnableOutput], ABC):
    @traceable
    @abstractmethod
    def invoke(self, input: TRunnableInput) -> TRunnableOutput:
        pass

    @traceable
    @abstractmethod
    def batch(self, inputs: list[TRunnableInput]) -> list[TRunnableOutput]:
        pass

    @traceable
    def __call__(self, input: TRunnableInput) -> TRunnableOutput:
        return self.invoke(input)


class DocumentRetriever(BaseRunnable[str, str]):
    pass


class HighLevelContextDocumentRetriever(DocumentRetriever):
    DEFAULT_INDEX_NAME = "high_level_context_index"

    def __init__(self, db: FAISS, index_name: str = DEFAULT_INDEX_NAME):
        super().__init__()
        self.__index_name = index_name
        self.__db = db

        retriever = self.__db.as_retriever(search_kwargs={"k": 3})

        self.__retriever_chain = retriever | self.__format_docs

    def __format_docs(self, docs: list[Document]) -> str:
        return ''.join(
            [d.page_content + END_DOCUMENT_SPLIT_SEPARATOR for d in docs]
        )

    @traceable(run_type="retriever")
    def invoke(self, query: str) -> str:
        return self.__retriever_chain.invoke(query)

    @traceable(run_type="retriever")
    def batch(self, queries: list[str]) -> list[str]:
        return self.__retriever_chain.batch(queries)

    def save(self, folder_path: str):
        self.__db.save_local(folder_path, self.__index_name)

    @classmethod
    def from_local(
        cls,
        folder_path: str,
        index_name: str = DEFAULT_INDEX_NAME,
    ):
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local(
            folder_path, embeddings, index_name, allow_dangerous_deserialization=True
        )
        return cls(db, index_name)

    @classmethod
    def from_document_file(
        cls, file_path: str, index_name: str = DEFAULT_INDEX_NAME
    ) -> "HighLevelContextDocumentRetriever":
        documents = cls.__load_documents(file_path)
        embeddings = OpenAIEmbeddings()

        db = FAISS.from_documents(documents, embeddings)

        return cls(db, index_name)

    @classmethod
    def __load_documents(cls, file_path: str) -> list[Document]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if os.path.isdir(file_path):
            raise ValueError("File path must be a file, not a directory.")

        loader = TextLoader(file_path)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        split_documents = text_splitter.split_documents(raw_documents)
        return split_documents


class CommitMessageGenerationChain(
    BaseRunnable[CommitMessageGenerationPromptInputModel, str]
):
    pass


class LowLevelContextCommitMessageGenerationChain(CommitMessageGenerationChain):
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__()

        prompt = PromptTemplate.from_template(LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    @traceable(run_type="llm")
    def invoke(self, prompt_input: CommitMessageGenerationPromptInputModel) -> str:
        return self.__chain.invoke(
            {"diff": prompt_input.diff, "source_code": prompt_input.source_code}
        )

    @traceable(run_type="llm")
    def batch(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[str]:
        return self.__chain.batch(
            [{"diff": pi.diff, "source_code": pi.source_code} for pi in prompt_inputs]
        )


class HighLevelContextCommitMessageGenerationChain(CommitMessageGenerationChain):
    def __init__(
        self,
        cmg_model: str,
        document_query_text_model: str,
        document_retriever: DocumentRetriever,
        cmg_temperature: float = 0.7,
        document_query_text_temperature: float = 0.7,
    ):
        super().__init__()

        document_query_text_prompt = PromptTemplate.from_template(
            DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE
        )

        document_query_text_llm = ChatOpenAI(
            model=document_query_text_model, temperature=document_query_text_temperature
        )
        document_query_text_output_parser = StrOutputParser()

        self.__high_level_context_chain: RunnableSerializable[str, str] = (
            {"source_code": RunnablePassthrough()}
            | document_query_text_prompt
            | document_query_text_llm
            | document_query_text_output_parser
            | document_retriever
        )

        cmg_prompt = PromptTemplate.from_template(
            HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE
        )
        cmg_llm = ChatOpenAI(model=cmg_model, temperature=cmg_temperature)
        cmg_output_parser = StrOutputParser()

        self.__cmg_chain = cmg_prompt | cmg_llm | cmg_output_parser

    def __get_high_level_context(self, source_code: str) -> str:
        return self.__high_level_context_chain.invoke(source_code)

    @traceable(run_type="llm")
    def get_high_level_context(self, source_code: str) -> str:
        # Testing purpose
        return self.__get_high_level_context(source_code)

    @traceable(run_type="llm")
    def invoke(self, prompt_input: CommitMessageGenerationPromptInputModel) -> str:

        context = self.__get_high_level_context(prompt_input.source_code)

        return self.__cmg_chain.invoke({"diff": prompt_input.diff, "context": context})

    @traceable(run_type="llm")
    def batch(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[str]:
        contexts = self.__high_level_context_chain.batch(
            [pi.source_code for pi in prompt_inputs]
        )

        return self.__cmg_chain.batch(
            [
                {"diff": pi.diff, "context": context}
                for pi, context in zip(prompt_inputs, contexts)
            ]
        )


class BaseDataGenerationChain(BaseRunnable[DataGenerationPromptInputModel, str]):
    pass


class DataGenerationChain(BaseDataGenerationChain):
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__()

        prompt = PromptTemplate.from_template(DATA_GENERATION_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

        self.__original_random_state = None

    def __seed_random(self):
        # generate random seed based on current time and current machine entropy
        self.__original_random_state = random.getstate()
        seed_value = int(time.time() * 1000) + int.from_bytes(os.urandom(8), "little")
        random.seed(seed_value)

    def __reset_random(self):
        if self.__original_random_state is not None:
            random.setstate(self.__original_random_state)
            self.__original_random_state = None

    def __get_random_section_order(self) -> str:
        return ", ".join(str(i) for i in random.sample(range(5, 31), 3))

    @traceable(run_type="llm")
    def invoke(self, prompt_input: DataGenerationPromptInputModel) -> str:
        self.__seed_random()

        section_order_string = self.__get_random_section_order()

        result = self.__chain.invoke(
            {
                "github_url": prompt_input.github_url,
                "source_code": prompt_input.source_code,
                "section_order_string": section_order_string,
                "requirement_id_format": random.choice(RANDOM_REQUIREMENT_ID_FORMATS),
            }
        )

        self.__reset_random()

        return result

    @traceable(run_type="llm")
    def batch(self, prompt_inputs: list[DataGenerationPromptInputModel]) -> list[str]:
        self.__seed_random()

        results = self.__chain.batch(
            [
                {
                    "github_url": pi.github_url,
                    "source_code": pi.source_code,
                    "section_order_string": self.__get_random_section_order(),
                    "requirement_id_format": random.choice(
                        RANDOM_REQUIREMENT_ID_FORMATS
                    ),
                }
                for pi in prompt_inputs
            ]
        )

        self.__reset_random()

        return results
