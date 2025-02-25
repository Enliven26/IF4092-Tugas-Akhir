import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import jsonpickle

from autocommit.core.chains import (
    CommitMessageGenerationChain,
    GetHighLevelContextInputModel,
    HighLevelContextChain,
)
from autocommit.core.enums import DiffVersion
from autocommit.core.git import IGit
from autocommit.core.models import (
    CommitDataModel,
    CommitMessageGenerationPromptInputModel,
)
from autocommit.core.parsers.git import IDiffParser
from autocommit.core.parsers.language.base import ICodeParser
from autocommit_evaluation.cmg.constants import (
    DEFAULT_EVALUATION_OUTPUT_FILE_NAME,
    DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME,
)
from autocommit_evaluation.cmg.models import (
    CommitMessageGenerationResultModel,
    EvaluationResultModel,
)


class ICommitMessageGenerator(ABC):
    @abstractmethod
    def generate_commit_messages(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[CommitMessageGenerationResultModel]:
        pass


class CommitMessageGenerator(ICommitMessageGenerator):
    def __init__(self, id: str, chain: CommitMessageGenerationChain):
        super().__init__()
        self.id = id
        self.__chain = chain

    def generate_commit_messages(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[CommitMessageGenerationResultModel]:
        commit_messages = self.__chain.batch(prompt_inputs)

        results: list[CommitMessageGenerationResultModel] = []

        for commit_message in commit_messages:
            result = CommitMessageGenerationResultModel()
            result.generator_id = self.id
            result.commit_message = commit_message

            results.append(result)

        return results


class IEvaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        commits: list[CommitDataModel],
        parent_output_path: str,
    ):
        pass


class Evaluator(IEvaluator):
    EVALUATION_OUTPUT_FILE_NAME = DEFAULT_EVALUATION_OUTPUT_FILE_NAME
    HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME = DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME

    def __init__(
        self,
        git: IGit,
        diff_parser: IDiffParser,
        code_parser: ICodeParser,
    ):
        super().__init__()
        self.__git: IGit = git
        self.__diff_parser: IDiffParser = diff_parser
        self.__code_parser: ICodeParser = code_parser

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

            if (file_content is None):
                pass
            
            new_implementations = self.__code_parser.get_declarations(
                file_content, file_diff.line_ranges
            )

            file_info = f"{file_diff.file_path} ({file_diff.version})"
            implementation = file_info + "\n" + new_implementations

            implementations.append(implementation)

        return "\n".join(implementations)

    def __get__high_level_context_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(
            parent_path, timestamp, self.__class__.HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME
        )

    def __get__evaluation_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(
            parent_path, timestamp, self.__class__.EVALUATION_OUTPUT_FILE_NAME
        )

    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)

    def __get_jira_ticket_id(self, commit: CommitDataModel) -> Optional[str]:
        commit_message = self.__git.get_commit_message(
            commit.repository_path, commit.commit_hash
        )

        match = re.search(r"\b([A-Z]+-\d+)\b", commit_message)
        return match.group(1) if match else None

    def classify_diffs(
        self,
        chain: CommitMessageGenerationChain,
        commits: list[CommitDataModel],
        parent_context_path: str,
        parent_output_path: str,
    ):
        # This is for testing purpose
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        inputs: list[dict[str, str]] = []

        for commit in commits:
            input = {}

            current_commit_hash = commit.commit_hash
            previous_commit_hash = f"{current_commit_hash}~1"

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

            input["diff"] = diff
            input["source_code"] = relevant_source_code
            input["context_file_path"] = os.path.join(
                parent_context_path, commit.get_context_file_relative_path()
            )
            input["vector_store_path"] = os.path.join(
                parent_context_path, commit.get_vector_store_relative_path()
            )

            inputs.append(input)

        results = chain.classify_diff_batch(inputs)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)

    def get_high_level_contexts(
        self,
        chain: HighLevelContextChain,
        commits: list[CommitDataModel],
        parent_context_path: str,
        parent_output_path: str,
    ):
        output_path = self.__get__high_level_context_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        inputs: list[GetHighLevelContextInputModel] = []

        for commit in commits:
            current_commit_hash = commit.commit_hash
            previous_commit_hash = f"{current_commit_hash}~1"

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

            prompt_input = GetHighLevelContextInputModel()
            prompt_input.source_code = relevant_source_code
            prompt_input.diff = diff
            prompt_input.context_file_path = os.path.join(
                parent_context_path, commit.get_context_file_relative_path()
            )
            prompt_input.vector_store_path = os.path.join(
                parent_context_path, commit.get_vector_store_relative_path()
            )

            inputs.append(prompt_input)

        results = chain.batch(inputs)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)

    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        commits: list[CommitDataModel],
        parent_context_path: str,
        parent_output_path: str,
    ):
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        prompt_inputs: list[CommitMessageGenerationPromptInputModel] = []
        results: list[EvaluationResultModel] = []

        for commit in commits:
            current_commit_hash = commit.commit_hash
            previous_commit_hash = f"{current_commit_hash}~1"

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

            prompt_input = CommitMessageGenerationPromptInputModel()
            prompt_input.diff = diff
            prompt_input.source_code = relevant_source_code
            prompt_input.context_file_path = os.path.join(
                parent_context_path, commit.get_context_file_relative_path()
            )
            prompt_input.vector_store_path = os.path.join(
                parent_context_path, commit.get_vector_store_relative_path()
            )
            prompt_input.id = commit.id

            prompt_inputs.append(prompt_input)

            result = EvaluationResultModel()
            result.evaluation_id = commit.id
            result.commit_url = f"{commit.repository_url}/commit/{commit.commit_hash}"
            result.jira_url = (
                f"{commit.jira_url}/browse/{self.__get_jira_ticket_id(commit)}"
            )
            result.included_file_paths = commit.included_file_paths

            results.append(result)

        for generator in generators:
            generation_results = generator.generate_commit_messages(prompt_inputs)

            for result, generation_result in zip(results, generation_results):
                result.generation_results.append(generation_result)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)
