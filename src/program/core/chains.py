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
    DEFAULT_CMG_TEMPERATURE,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_HIGH_LEVEL_CONTEXT_INDEX_NAME,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE,
    END_DOCUMENT_SPLIT_SEPARATOR,
    FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    HIGH_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE,
    HIGH_LEVEL_CONTEXT_FILTER_PROMPT_TEMPLATE,
    LOW_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE,
)
from core.models import (
    CommitMessageGenerationPromptInputModel,
    GetHighLevelContextInputModel,
    HighLevelContextDiffClassificationInputModel,
    JiraContextDocumentRetrieverInputModel,
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


class JiraContextDocumentRetriever(
    DocumentRetriever[JiraContextDocumentRetrieverInputModel]
):

    def __init__(
        self,
        db: FAISS,
        llm_filter_model: str,
        llm_filter_temperature: int = DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_HIGH_LEVEL_CONTEXT_INDEX_NAME,
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
        self, input: JiraContextDocumentRetrieverInputModel
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
    def invoke(self, input: JiraContextDocumentRetrieverInputModel) -> str:
        return self.__retriever_chain.invoke(input)

    @traceable(run_type="retriever")
    def batch(self, inputs: list[JiraContextDocumentRetrieverInputModel]) -> list[str]:
        return self.__retriever_chain.batch(inputs)

    def save(self, folder_path: str):
        self.__db.save_local(folder_path, self.__index_name)

    @classmethod
    def from_local(
        cls,
        folder_path: str,
        embedding_model: str,
        llm_filter_model: str,
        llm_filter_temperature: int = DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_HIGH_LEVEL_CONTEXT_INDEX_NAME,
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
        llm_filter_temperature: int = DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
        index_name: str = DEFAULT_HIGH_LEVEL_CONTEXT_INDEX_NAME,
    ) -> "JiraContextDocumentRetriever":
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
            separators=[END_DOCUMENT_SPLIT_SEPARATOR], keep_separator=False
        )
        split_documents = text_splitter.split_documents(raw_documents)
        return split_documents


class LowLevelContextDiffClassifierChain(BaseRunnable[str, str]):
    def __init__(
        self, model: str, temperature: float = DEFAULT_DIFF_CLASSIFIER_TEMPERATURE
    ):
        super().__init__()

        prompt = PromptTemplate.from_template(
            LOW_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE
        )
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    @traceable(run_type="llm")
    def invoke(self, diff: str) -> str:
        return self.__chain.invoke(diff)

    @traceable(run_type="llm")
    def batch(self, diffs: list[str]) -> list[str]:
        return self.__chain.batch(diffs)


class HighLevelContextDiffClassifierChain(
    BaseRunnable[HighLevelContextDiffClassificationInputModel, str]
):
    def __init__(
        self, model: str, temperature: float = DEFAULT_DIFF_CLASSIFIER_TEMPERATURE
    ):
        super().__init__()

        prompt = PromptTemplate.from_template(
            HIGH_LEVEL_CONTEXT_DIFF_CLASSIFIER_PROMPT_TEMPLATE
        )
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__chain = prompt | llm | output_parser

    @traceable(run_type="llm")
    def invoke(self, input: HighLevelContextDiffClassificationInputModel) -> str:
        return self.__chain.invoke({"diff": input.diff, "context": input.context})

    @traceable(run_type="llm")
    def batch(
        self, inputs: list[HighLevelContextDiffClassificationInputModel]
    ) -> list[str]:
        return self.__chain.batch(
            [{"diff": input.diff, "context": input.context} for input in inputs]
        )


class CommitMessageGenerationChain(
    BaseRunnable[CommitMessageGenerationPromptInputModel, str]
):
    @abstractmethod
    def classify_diff(self, input: dict[str, str]) -> str:
        pass

    @abstractmethod
    def classify_diff_batch(self, inputs: list[dict[str, str]]) -> list[str]:
        pass


class LowLevelContextCommitMessageGenerationChain(CommitMessageGenerationChain):
    def __init__(
        self,
        diff_classifier: BaseRunnable[str, str],
        model: str,
        temperature: float = DEFAULT_CMG_TEMPERATURE,
    ):
        super().__init__()

        prompt = PromptTemplate.from_template(
            FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE
        )
        llm = ChatOpenAI(model=model, temperature=temperature)
        output_parser = StrOutputParser()

        self.__diff_classifier = diff_classifier
        self.__chain = (
            RunnableLambda(
                lambda x: {
                    "diff": x["diff"],
                    "source_code": x["source_code"],
                    "type": self.__classify_diff(x["diff"]),
                }
            )
            | prompt
            | llm
            | output_parser
        )

    def __classify_diff(self, diff: str) -> str:
        return self.__diff_classifier.invoke(diff)

    def classify_diff(self, input: dict[str, str]) -> str:
        return self.__classify_diff(input["diff"])

    def classify_diff_batch(self, diffs: list[dict[str, str]]) -> list[str]:
        return self.__diff_classifier.batch([diff["diff"] for diff in diffs])

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


class HighLevelContextChain(BaseRunnable[GetHighLevelContextInputModel, str]):

    def __init__(
        self,
        llm_query_text_model: str,
        embeddings_model: str,
        llm_filter_model: str,
        llm_query_text_temperature: float = DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
        llm_filter_temperature: float = DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    ):
        document_query_text_prompt = PromptTemplate.from_template(
            DOCUMENT_QUERY_TEXT_PROMPT_TEMPLATE
        )

        document_query_text_llm = ChatOpenAI(
            model=llm_query_text_model, temperature=llm_query_text_temperature
        )

        document_query_text_output_parser = StrOutputParser()

        self.__document_retriever: Optional[
            DocumentRetriever[JiraContextDocumentRetrieverInputModel]
        ] = None

        self.__embeddings_model = embeddings_model
        self.__llm_filter_model = llm_filter_model
        self.__llm_filter_temperature = llm_filter_temperature

        self.__chain: RunnableSerializable[dict, str] = (
            RunnablePassthrough()
            | {
                "query": (
                    RunnablePassthrough()
                    | document_query_text_prompt
                    | document_query_text_llm
                    | document_query_text_output_parser
                ),
                "diff": RunnableLambda(lambda x: x["diff"]),
                "context_file_path": RunnableLambda(lambda x: x["context_file_path"]),
                "vector_store_path": RunnableLambda(lambda x: x["vector_store_path"]),
            }
            | self.__retrieve_context
        )

    def __retrieve_context(self, input: dict) -> str:
        retriever_input = JiraContextDocumentRetrieverInputModel()
        retriever_input.query = input["query"]
        retriever_input.diff = input["diff"]

        self.__document_retriever = self.__create_retriever_if_not_exist(
            input["context_file_path"], input["vector_store_path"]
        )

        return self.__document_retriever.invoke(retriever_input)

    def __create_retriever_if_not_exist(
        self,
        context_file_path: str,
        vector_store_path: str,
    ) -> DocumentRetriever:
        document_retriever: JiraContextDocumentRetriever = None

        if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
            os.makedirs(vector_store_path, exist_ok=True)
            document_retriever = JiraContextDocumentRetriever.from_document_file(
                context_file_path,
                self.__embeddings_model,
                self.__llm_filter_model,
                self.__llm_filter_temperature,
            )
            document_retriever.save(vector_store_path)

        else:
            document_retriever = JiraContextDocumentRetriever.from_local(
                vector_store_path,
                self.__embeddings_model,
                self.__llm_filter_model,
                self.__llm_filter_temperature,
            )

        return document_retriever

    def __get_high_level_context(
        self,
        source_code: str,
        diff: str,
        context_file_path: str,
        vector_store_path: str,
    ) -> str:
        return self.__chain.invoke(
            {
                "source_code": source_code,
                "diff": diff,
                "context_file_path": context_file_path,
                "vector_store_path": vector_store_path,
            }
        )

    def __get_high_level_context_batch(self, inputs: list[dict[str, str]]) -> list[str]:
        return self.__chain.batch(inputs)

    def __set_retriever(
        self,
        embeddings_model: str,
        llm_model: str,
        context_file_path: str,
        vector_store_path: str,
    ):
        self.__document_retriever = self.__create_retriever_if_not_exist(
            embeddings_model, llm_model, context_file_path, vector_store_path
        )

    @traceable(run_type="llm")
    def invoke(self, input: GetHighLevelContextInputModel) -> str:
        return self.__get_high_level_context(
            input.source_code,
            input.diff,
            input.context_file_path,
            input.vector_store_path,
        )

    @traceable(run_type="llm")
    def batch(self, inputs: list[GetHighLevelContextInputModel]) -> list[str]:
        dict_inputs = [
            {
                "source_code": input.source_code,
                "diff": input.diff,
                "context_file_path": input.context_file_path,
                "vector_store_path": input.vector_store_path,
            }
            for input in inputs
        ]
        return self.__get_high_level_context_batch(dict_inputs)


class HighLevelContextCommitMessageGenerationChain(CommitMessageGenerationChain):
    def __init__(
        self,
        diff_classifier: BaseRunnable[
            HighLevelContextDiffClassificationInputModel, str
        ],
        high_level_context_chain: HighLevelContextChain,
        prompt_template: str,
        cmg_model: str,
        cmg_temperature: float = DEFAULT_CMG_TEMPERATURE,
    ):
        super().__init__()

        self.__high_level_context_chain = high_level_context_chain

        cmg_prompt = PromptTemplate.from_template(prompt_template)
        cmg_llm = ChatOpenAI(model=cmg_model, temperature=cmg_temperature)
        cmg_output_parser = StrOutputParser()

        self.__diff_classifier = diff_classifier

        self.__cmg_chain: RunnableSerializable[dict, str] = (
            RunnableLambda(
                lambda x: {
                    "diff": x["diff"],
                    "source_code": x["source_code"],
                    "context_file_path": x["context_file_path"],
                    "vector_store_path": x["vector_store_path"],
                    "context": self.__retrieve_context(x),
                }
            )
            | RunnableLambda(
                lambda x: {
                    "diff": x["diff"],
                    "context": x["context"],
                    "type": self.__classify_diff(x["diff"], x["context"]),
                }
            )
            | cmg_prompt
            | cmg_llm
            | cmg_output_parser
        )

    def __retrieve_context(self, input: dict) -> str:
        get_high_level_context_input = GetHighLevelContextInputModel()
        get_high_level_context_input.diff = input["diff"]
        get_high_level_context_input.source_code = input["source_code"]
        get_high_level_context_input.context_file_path = input["context_file_path"]
        get_high_level_context_input.vector_store_path = input["vector_store_path"]

        return self.__high_level_context_chain.invoke(get_high_level_context_input)

    def __retrieve_context_batch(self, inputs: list[dict]) -> list[str]:
        get_high_level_context_inputs = []

        for input in inputs:
            get_high_level_context_input = GetHighLevelContextInputModel()
            get_high_level_context_input.diff = input["diff"]
            get_high_level_context_input.source_code = input["source_code"]
            get_high_level_context_input.context_file_path = input["context_file_path"]
            get_high_level_context_input.vector_store_path = input["vector_store_path"]

            get_high_level_context_inputs.append(get_high_level_context_input)

        return self.__high_level_context_chain.batch(get_high_level_context_inputs)

    def __classify_diff(self, diff: str, context: str) -> str:
        input = HighLevelContextDiffClassificationInputModel()
        input.diff = diff
        input.context = context

        return self.__diff_classifier.invoke(input)

    def classify_diff(self, input: dict[str, str]) -> str:
        context = self.__retrieve_context(input)
        self.__classify_diff(input["diff"], context)

    def classify_diff_batch(self, inputs: list[dict[str, str]]) -> list[str]:
        classifier_inputs: list[HighLevelContextDiffClassifierChain] = []
        contexts = self.__retrieve_context_batch(inputs)

        for input, context in zip(inputs, contexts):
            classifier_input = HighLevelContextDiffClassificationInputModel()
            classifier_input.diff = input["diff"]
            classifier_input.context = context
            classifier_inputs.append(classifier_input)

        return self.__diff_classifier.batch(classifier_inputs)

    def set_retriever(
        self, retriever: DocumentRetriever[JiraContextDocumentRetrieverInputModel]
    ):
        self.__high_level_context_chain.__document_retriever = retriever

    def set_retriever_by_vectorstore(
        self,
        embeddings_model: str,
        llm_model: str,
        context_file_path: str,
        vector_store_path: str,
    ):
        self.__high_level_context_chain.__set_retriever(
            embeddings_model, llm_model, context_file_path, vector_store_path
        )

    @traceable(run_type="llm")
    def invoke(self, prompt_input: CommitMessageGenerationPromptInputModel) -> str:
        return self.__cmg_chain.invoke(
            {
                "diff": prompt_input.diff,
                "source_code": prompt_input.source_code,
                "context_file_path": prompt_input.context_file_path,
                "vector_store_path": prompt_input.vector_store_path,
            }
        )

    @traceable(run_type="llm")
    def batch(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[str]:
        return self.__cmg_chain.batch(
            [
                {
                    "diff": pi.diff,
                    "source_code": pi.source_code,
                    "context_file_path": pi.context_file_path,
                    "vector_store_path": pi.vector_store_path,
                }
                for pi in prompt_inputs
            ]
        )
