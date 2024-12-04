import os
from abc import ABC, abstractmethod

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from core.constants import (
    DATA_GENERATION_PROMPT_TEMPLATE,
    DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE,
    HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.models import CommitMessageGenerationPromptInputModel


class IHighLevelContextDocumentRetriever(ABC):
    @abstractmethod
    def search(self, query: str) -> str:
        pass


class HighLevelContextDocumentRetriever(IHighLevelContextDocumentRetriever):
    DEFAULT_INDEX_NAME = "high_level_context_index"

    def __init__(self, db: FAISS, index_name: str = DEFAULT_INDEX_NAME):
        super().__init__()
        self.__index_name = index_name
        self.__db = db
        self.__retriever = self.__db.as_retriever()

    def search(self, query: str) -> str:
        return self.__retriever.invoke(query)

    def save(self, folder_path: str):
        self.__db.save_local(folder_path, self.__index_name)

    @classmethod
    def from_local(
        cls,
        folder_path: str,
        embeddings: OpenAIEmbeddings,
        index_name: str = DEFAULT_INDEX_NAME,
    ):
        db = FAISS.load_local(folder_path, embeddings, index_name)
        return cls(db, index_name)

    @classmethod
    def from_document_file(cls, file_path: str, index_name: str = DEFAULT_INDEX_NAME):
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


class ICommitMessageGenerationChain(ABC):
    @abstractmethod
    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> str:
        pass


class LowLevelContextCommitMessageGenerationChain(ICommitMessageGenerationChain):
    def __init__(self, model: str, temperature: float = 0.7):
        super().__init__()

        prompt = PromptTemplate.from_template(LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> str:
        return self.__chain.invoke({"diff": prompt_input.diff})


class HighLevelContextCommitMessageGenerationChain(ICommitMessageGenerationChain):
    def __init__(
        self,
        cmg_model: str,
        document_query_text_model: str,
        document_retriever: IHighLevelContextDocumentRetriever,
        cmg_temperature: float = 0.7,
        document_query_text_temperature: float = 0.7,
    ):
        super().__init__()

        self.__document_retriever = document_retriever

        document_query_text_prompt = PromptTemplate.from_template(
            DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE
        )

        document_query_text_llm = ChatOpenAI(
            model=document_query_text_model, temperature=document_query_text_temperature
        )
        document_query_text_output_parser = StrOutputParser()

        self.__document_query_text_chain = (
            document_query_text_prompt
            | document_query_text_llm
            | document_query_text_output_parser
        )

        cmg_prompt = PromptTemplate.from_template(
            HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE
        )
        cmg_llm = ChatOpenAI(model=cmg_model, temperature=cmg_temperature)
        cmg_output_parser = StrOutputParser()

        self.__cmg_chain = cmg_prompt | cmg_llm | cmg_output_parser

    def __get_high_level_context(self, source_code: str) -> str:
        query_text = self.__document_query_text_chain.invoke(
            {"source_code": source_code}
        )

        return self.__document_retriever.search(query_text)

    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> str:

        context = self.__get_high_level_context(prompt_input.source_code)

        return self.__cmg_chain.invoke({"diff": prompt_input.diff, "context": context})


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
