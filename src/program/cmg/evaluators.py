import json
import os
from abc import ABC, abstractmethod
from datetime import datetime

import jsonpickle

from cmg.models import (
    CommitMessageGenerationResultModel,
    EvaluationModel,
    EvaluationResultModel,
)
from core.chains import (
    CommitMessageGenerationChain,
    GetHighLevelContextInputModel,
    HighLevelContextCommitMessageGenerationChain,
)
from core.enums import DiffVersion
from core.git import IGit
from core.models import CommitMessageGenerationPromptInputModel
from core.parsers.git import IDiffParser
from core.parsers.language.base import ICodeParser


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
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        pass


class Evaluator(IEvaluator):
    EVALUATION_OUTPUT_FILE_NAME = "evaluation.json"
    HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME = "highlevelcontext.json"

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

            new_implementations = self.__code_parser.get_declarations(
                file_content, file_diff.line_ranges
            )

            file_info = f"{file_diff.file_path} ({file_diff.version})"
            implementation = file_info + "\n" + "\n".join(new_implementations)

            implementations.append(implementation)

        return "\n".join(implementations)

    def __get__evaluation_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(
            parent_path, timestamp, self.__class__.EVALUATION_OUTPUT_FILE_NAME
        )

    def __get__evaluation_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(
            parent_path, timestamp, self.__class__.HIGH_LEVEL_CONTEXT_OUTPUT_FILE_NAME
        )

    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)

    def classify_diffs(
        self,
        chain: CommitMessageGenerationChain,
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        # This is for testing purpose
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        diffs: list[str] = []

        for evaluation in evaluation_data:
            current_commit_hash = evaluation.current_commit_hash
            previous_commit_hash = f"{current_commit_hash}~1"

            diff = self.__git.get_diff(
                evaluation.repository_path,
                previous_commit_hash,
                current_commit_hash,
                evaluation.included_file_paths,
            )

            diffs.append(diff)

        results = chain.classify_diff_batch(diffs)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)

    def get_high_level_contexts(
        self,
        chain: HighLevelContextCommitMessageGenerationChain,
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        # This is for testing purpose
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        inputs: list[GetHighLevelContextInputModel] = []

        for evaluation in evaluation_data:
            current_commit_hash = evaluation.current_commit_hash
            previous_commit_hash = (
                evaluation.previous_commit_hash or f"{current_commit_hash}~1"
            )

            diff = self.__git.get_diff(
                evaluation.repository_path,
                previous_commit_hash,
                current_commit_hash,
                evaluation.included_file_paths,
            )

            relevant_source_code = self.__get_implementations(
                evaluation.repository_path,
                previous_commit_hash,
                current_commit_hash,
                evaluation.included_file_paths,
                diff,
            )

            input = GetHighLevelContextInputModel()
            input.source_code = relevant_source_code
            input.diff = diff

            inputs.append(input)

        results = chain.get_high_level_context_batch(inputs)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)

    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        prompt_inputs: list[CommitMessageGenerationPromptInputModel] = []
        results: list[EvaluationResultModel] = []

        for evaluation in evaluation_data:
            current_commit_hash = evaluation.current_commit_hash
            previous_commit_hash = f"{current_commit_hash}~1"

            diff = self.__git.get_diff(
                evaluation.repository_path,
                previous_commit_hash,
                current_commit_hash,
                evaluation.included_file_paths,
            )

            relevant_source_code = self.__get_implementations(
                evaluation.repository_path,
                previous_commit_hash,
                current_commit_hash,
                evaluation.included_file_paths,
                diff,
            )

            prompt_input = CommitMessageGenerationPromptInputModel()
            prompt_input.diff = diff
            prompt_input.source_code = relevant_source_code

            prompt_inputs.append(prompt_input)

            result = EvaluationResultModel()
            result.evaluation_id = evaluation.id
            results.append(result)

        for generator in generators:
            generation_results = generator.generate_commit_messages(prompt_inputs)

            for result, generation_result in zip(results, generation_results):
                result.generation_results.append(generation_result)

        json_string = jsonpickle.encode(results, unpicklable=False)

        with open(output_path, "w") as file:
            file.write(json_string)
