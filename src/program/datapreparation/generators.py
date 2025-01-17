import os
import re
from abc import ABC, abstractmethod
from datetime import datetime

import jsonpickle

from core.chains import DiffContextDocumentRetriever, DocumentRetriever
from core.constants import DEFAULT_EMBEDDINGS_MODEL, DEFAULT_LLM_MODEL
from core.enums import DiffVersion
from core.git import IGit
from core.jira import IJira
from core.models import CommitDataModel, DiffContextDocumentRetrieverInputModel
from core.parsers.git import IDiffParser
from core.parsers.language.base import ICodeParser
from datapreparation.models import ExampleGenerationResultModel


class IContextGenerator(ABC):
    @abstractmethod
    def generate_context(self, commits: list[CommitDataModel], parent_output_path: str):
        pass


class JiraContextGenerator(IContextGenerator):
    def __init__(self, git: IGit, jira: IJira):
        super().__init__()
        self.__git = git
        self.__jira = jira

    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)

    def __get_jira_ticket_context(self, commit: CommitDataModel) -> str:
        commit_message = self.__git.get_commit_message(
            commit.repository_path, commit.commit_hash
        )

        match = re.search(r"\b([A-Z]+-\d+)\b", commit_message)
        if match:
            jira_ticket_id = match.group(1)
            ticket_content = self.__jira.get_ticket_content(
                commit.jira_url, jira_ticket_id
            )
            return ticket_content

        else:
            raise ValueError(
                f"No JIRA ticket found in commit message: {commit_message}"
            )

    def __generate_context_for_commits(self, commits: list[CommitDataModel]) -> str:
        contexts = []
        for commit in commits:
            context = self.__get_jira_ticket_context(commit)
            contexts.append(context)

        return "n".join(contexts)

    def __write_context_to_file(
        self, parent_output_path: str, relative_path: str, file_name: str, context: str
    ):
        full_path = os.path.join(parent_output_path, relative_path, file_name)
        self.__create_folder_if_not_exist(full_path)

        with open(full_path, "w", encoding="utf-8") as file:
            file.write(context)

    def generate_context(self, commits: list[CommitDataModel], parent_output_path: str):
        grouped_commits: dict[str, list[CommitDataModel]] = {}

        for commit in commits:
            relative_path = commit.get_context_relative_path(commit)

            if relative_path not in grouped_commits:
                grouped_commits[relative_path] = []

            grouped_commits[relative_path].append(commit)

        for relative_path, commits in grouped_commits.items():
            context = self.__generate_context_for_commits(commits)
            self.__write_context_to_file(
                parent_output_path,
                relative_path,
                CommitDataModel.CONTEXT_FILE_NAME,
                context,
            )


class IExampleGenerator(ABC):
    @abstractmethod
    def generate_examples(
        self, examples: list[CommitDataModel], parent_output_path: str
    ):
        pass


class ExampleGenerator(IExampleGenerator):
    OUTPUT_FILE_NAME = "examples.json"

    def __init__(
        self,
        git: IGit,
        diff_parser: IDiffParser,
        code_parser: ICodeParser,
    ):
        super().__init__()
        self.__git = git
        self.__diff_parser = diff_parser
        self.__code_parser = code_parser

    def __get_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(parent_path, timestamp, self.__class__.OUTPUT_FILE_NAME)

    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)

    def __get_implementations(
        self,
        source_repo_path: str,
        previous_commit_hash: str,
        current_commit_hash: str,
        included_file_paths: list[str],
        diff: str,
    ) -> str:
        commit_map = {
            DiffVersion.OLD: previous_commit_hash,
            DiffVersion.NEW: current_commit_hash,
        }

        file_diffs = self.__diff_parser.get_diff_lines(diff, included_file_paths)

        implementations: list[str] = []

        for file_diff in file_diffs:
            file_content = self.__git.get_file_content(
                source_repo_path, commit_map[file_diff.version], file_diff.file_path
            )

            new_implementation = self.__code_parser.get_declarations(
                file_content, file_diff.line_ranges
            )

            file_info = f"{file_diff.file_path} ({file_diff.version})"
            implementation = file_info + "\n" + new_implementation

            implementations.append(implementation)

        return "\n".join(implementations)

    def __create_retriever_if_not_exist(
        self,
        embeddings_model: str,
        llm_model: str,
        commit: CommitDataModel,
        parent_context_path: str,
    ) -> DocumentRetriever:
        context_file_path = os.path.join(
            parent_context_path, commit.get_context_relative_path()
        )
        vector_store_path = os.path.join(
            parent_context_path, commit.get_vector_store_relative_path()
        )

        document_retriever: DiffContextDocumentRetriever = None

        if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
            os.makedirs(vector_store_path, exist_ok=True)
            document_retriever = DiffContextDocumentRetriever.from_document_file(
                context_file_path, embeddings_model, llm_model
            )
            document_retriever.save(vector_store_path)

        else:
            document_retriever = DiffContextDocumentRetriever.from_local(
                vector_store_path, embeddings_model, llm_model
            )

        return document_retriever

    def generate_examples(
        self,
        commits: list[CommitDataModel],
        parent_context_path: str,
        parent_output_path: str,
        embeddings_model: str = DEFAULT_EMBEDDINGS_MODEL,
        llm_model: str = DEFAULT_LLM_MODEL,
    ):
        output_path = self.__get_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)
        results: list[ExampleGenerationResultModel] = []

        for commit in commits:
            current_commit_hash = commit.commit_hash
            previous_commit_hash = f"{current_commit_hash}^1"

            diff = self.__git.get_diff(
                commit.repository_path,
                previous_commit_hash,
                current_commit_hash,
                commit.included_file_paths,
            )

            relevant_source_code = self.__get_implementations(
                commit.repository_path,
                previous_commit_hash,
                current_commit_hash,
                commit.included_file_paths,
                diff,
            )

            result = ExampleGenerationResultModel()
            result.diff = diff
            result.source_code = relevant_source_code
            result.commit_message = self.__git.get_commit_message(
                commit.repository_path, commit.commit_hash
            )

            retriever = self.__create_retriever_if_not_exist(
                embeddings_model, llm_model, commit, parent_context_path
            )
            retriever_input = DiffContextDocumentRetrieverInputModel()
            retriever_input.diff = diff

            result.high_level_context = retriever.invoke(diff)

            results.append(result)

        json_string = jsonpickle.encode(results, unpicklable=False)
        with open(output_path, "w") as file:
            file.write(json_string)
