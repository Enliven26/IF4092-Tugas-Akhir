import os
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from langchain.output_parsers.boolean import BooleanOutputParser
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableSerializable,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langsmith import traceable

from core.constants import (
    DIFF_CLASSIFIER_PROMPT_TEMPLATE,
    DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE,
    END_DOCUMENT_SPLIT_SEPARATOR,
    HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE,
    LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.models import (
    CommitMessageGenerationPromptInputModel,
    DataGenerationPromptInputModel,
    DiffContextDocumentRetrieverInputModel,
    GetHighLevelContextInputModel,
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


TDocumentRetrieverInput = TypeVar("TDocumentRetrieverInput")


class DocumentRetriever(BaseRunnable[TDocumentRetrieverInput, str]):
    pass


class DiffContextDocumentRetriever(
    DocumentRetriever[DiffContextDocumentRetrieverInputModel]
):
    DEFAULT_INDEX_NAME = "high_level_context_index"
    DEFAULT_LLM_FILTER_TEMPERATURE = 0

    def __init__(
        self,
        db: FAISS,
        llm_filter_model: str,
        llm_filter_temperature: int = DEFAULT_LLM_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_INDEX_NAME,
    ):
        super().__init__()
        self.__index_name = index_name
        self.__db = db

        llm = ChatOpenAI(model=llm_filter_model, temperature=llm_filter_temperature)
        filter_prompt = PromptTemplate(
            template=HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE,
            input_variables=["question", "context", "diff"],
            output_parser=BooleanOutputParser(),
        )

        self.__retriever = self.__db.as_retriever(search_kwargs={"k": 6})
        self.__compresor = LLMChainFilter.from_llm(llm, filter_prompt)
        self.__retriever_chain = (
            self.__get_context | RunnablePassthrough() | self.__format_docs
        )

    def __get_context(
        self, input: DiffContextDocumentRetrieverInputModel
    ) -> list[Document]:
        docs = self.__retriever.invoke(input.query)
        self.__set_filter_input_getter(input.diff)
        return self.__compresor.compress_documents(docs, input.query)

    def __set_filter_input_getter(self, diff: str):
        def getter(query: str, doc: Document):
            return {"query": query, "context": doc.page_content, "diff": diff}

        self.__compresor.get_input = getter

    def __format_docs(self, docs: list[Document]) -> str:
        return "".join([d.page_content + END_DOCUMENT_SPLIT_SEPARATOR for d in docs])

    @traceable(run_type="retriever")
    def invoke(self, input: DiffContextDocumentRetrieverInputModel) -> str:
        return self.__retriever_chain.invoke(input)

    @traceable(run_type="retriever")
    def batch(self, inputs: list[DiffContextDocumentRetrieverInputModel]) -> list[str]:
        return self.__retriever_chain.batch(inputs)

    def save(self, folder_path: str):
        self.__db.save_local(folder_path, self.__index_name)

    @classmethod
    def from_local(
        cls,
        folder_path: str,
        embedding_model: str,
        llm_filter_model: str,
        llm_filter_temperature: int = DEFAULT_LLM_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_INDEX_NAME,
    ):
        embeddings = OpenAIEmbeddings(model=embedding_model)
        db = FAISS.load_local(
            folder_path,
            embeddings,
            index_name,
            allow_dangerous_deserialization=True,
        )
        return cls(db, llm_filter_model, llm_filter_temperature, index_name)

    @classmethod
    def from_document_file(
        cls,
        file_path: str,
        embeding_model: str,
        llm_filter_model: str,
        llm_filter_temperature: int = DEFAULT_LLM_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_INDEX_NAME,
    ) -> "DiffContextDocumentRetriever":
        documents = cls.__load_documents(file_path)
        embeddings = OpenAIEmbeddings(model=embeding_model)

        db = FAISS.from_documents(documents, embeddings)

        return cls(db, llm_filter_model, llm_filter_temperature, index_name)

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


class DiffClassifierChain(BaseRunnable[str, str]):
    def __init__(self, model: str, temperature: float = 0):
        super().__init__()

        prompt = PromptTemplate.from_template(DIFF_CLASSIFIER_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    @traceable(run_type="llm")
    def invoke(self, diff: str) -> str:
        return self.__chain.invoke(diff)

    @traceable(run_type="llm")
    def batch(self, diffs: list[str]) -> list[str]:
        return self.__chain.batch(diffs)


class CommitMessageGenerationChain(
    BaseRunnable[CommitMessageGenerationPromptInputModel, str]
):
    def __init__(self, diff_classifier: BaseRunnable[str, str]):
        super().__init__()
        self.__diff_classifier = diff_classifier

    def classify_diff(self, diff: str) -> str:
        return self.__diff_classifier.invoke(diff)

    def classify_diff_batch(self, diffs: list[str]) -> list[str]:
        return self.__diff_classifier.batch(diffs)


class LowLevelContextCommitMessageGenerationChain(CommitMessageGenerationChain):
    def __init__(
        self,
        diff_classifier: BaseRunnable[str, str],
        model: str,
        temperature: float = 0.7,
    ):
        super().__init__(diff_classifier)

        prompt = PromptTemplate.from_template(LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = (
            RunnableLambda(
                lambda x: {
                    "diff": x["diff"],
                    "source_code": x["source_code"],
                    "type": self.classify_diff(x["diff"]),
                }
            )
            | prompt
            | llm
            | output_parser
        )

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
        diff_classifier: BaseRunnable[str, str],
        prompt_template: str,
        cmg_model: str,
        document_query_text_model: str,
        cmg_temperature: float = 0.7,
        document_query_text_temperature: float = 0.55,
    ):
        super().__init__(diff_classifier)

        document_query_text_prompt = PromptTemplate.from_template(
            DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE
        )

        document_query_text_llm = ChatOpenAI(
            model=document_query_text_model, temperature=document_query_text_temperature
        )
        document_query_text_output_parser = StrOutputParser()

        self.__document_retriever: Optional[
            DocumentRetriever[DiffContextDocumentRetrieverInputModel]
        ] = None
        self.__high_level_context_chain: RunnableSerializable[dict, str] = (
            RunnablePassthrough()
            | {
                "query": (
                    RunnablePassthrough()
                    | document_query_text_prompt
                    | document_query_text_llm
                    | document_query_text_output_parser
                ),
                "diff": RunnableLambda(lambda x: x["diff"]),
            }
            | self.__retrieve_context
        )

        cmg_prompt = PromptTemplate.from_template(prompt_template)
        cmg_llm = ChatOpenAI(model=cmg_model, temperature=cmg_temperature)
        cmg_output_parser = StrOutputParser()

        self.__cmg_chain = (
            RunnableLambda(
                lambda x: {
                    "diff": x["diff"],
                    "context": self.__high_level_context_chain.invoke(x),
                    "type": self.classify_diff(x["diff"]),
                }
            )
            | cmg_prompt
            | cmg_llm
            | cmg_output_parser
        )

    def __retrieve_context(self, input: dict) -> str:
        retriever_input = DiffContextDocumentRetrieverInputModel()
        retriever_input.query = input["query"]
        retriever_input.diff = input["diff"]

        return self.__document_retriever.invoke(retriever_input)

    def __get_high_level_context(self, source_code: str, diff: str) -> str:
        return self.__high_level_context_chain.invoke(
            {"source_code": source_code, "diff": diff}
        )

    def __get_high_level_context_batch(self, inputs: list[dict[str, str]]) -> list[str]:
        return self.__high_level_context_chain.batch(inputs)

    def __validate_retriever(self):
        if self.__document_retriever is None:
            raise ValueError("Document retriever has not been set.")

    def set_retirever(
        self, retriever: DocumentRetriever[DiffContextDocumentRetrieverInputModel]
    ):
        self.__document_retriever = retriever

    @traceable(run_type="llm")
    def get_high_level_context(self, input: GetHighLevelContextInputModel) -> str:
        self.__validate_retriever()

        # Testing purpose
        return self.__get_high_level_context(input.source_code, input.diff)

    @traceable(run_type="llm")
    def get_high_level_context_batch(
        self, inputs: list[GetHighLevelContextInputModel]
    ) -> list[str]:
        self.__validate_retriever()

        dict_inputs = [
            {"source_code": input.source_code, "diff": input.diff} for input in inputs
        ]
        return self.__get_high_level_context_batch(dict_inputs)

    @traceable(run_type="llm")
    def invoke(self, prompt_input: CommitMessageGenerationPromptInputModel) -> str:
        self.__validate_retriever()

        return self.__cmg_chain.invoke(
            {"diff": prompt_input.diff, "source_code": prompt_input.source_code}
        )

    @traceable(run_type="llm")
    def batch(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[str]:
        self.__validate_retriever()

        return self.__cmg_chain.batch(
            [{"diff": pi.diff, "source_code": pi.source_code} for pi in prompt_inputs]
        )
