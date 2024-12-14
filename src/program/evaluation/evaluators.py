import json
import os
from abc import ABC, abstractmethod
from datetime import datetime

from core.chains import (
    HighLevelContextCommitMessageGenerationChain,
    ICommitMessageGenerationChain,
)
from core.enums import DiffVersion
from core.git import IGit
from core.models import CommitMessageGenerationPromptInputModel
from core.parsers import ICodeParser, IDiffParser
from evaluation.models import (
    CommitMessageGenerationResultModel,
    EvaluationModel,
    EvaluationResultModel,
)


class ICommitMessageGenerator(ABC):
    @abstractmethod
    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> CommitMessageGenerationResultModel:
        pass


class CommitMessageGenerator(ICommitMessageGenerator):
    def __init__(self, id: str, chain: ICommitMessageGenerationChain):
        super().__init__()
        self.id = id
        self.__chain = chain

    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> CommitMessageGenerationResultModel:
        commit_message = self.__chain.generate_commit_message(prompt_input)
        result = CommitMessageGenerationResultModel()
        result.generator_id = self.id
        result.commit_message = commit_message

        return result


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

            new_implementations = self.__code_parser.get_methods(
                file_content, file_diff.line_ranges
            )
            implementations.extend(new_implementations)

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

    def get_high_level_context(
        self,
        chain: HighLevelContextCommitMessageGenerationChain,
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        # This is for testing purpose
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        with open(output_path, "w") as file:
            file.write("[")

            for index, evaluation in enumerate(evaluation_data):
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

                result = chain.get_high_level_context(relevant_source_code)

                file.write(f"\n{json.dumps(result)}")
                if index < len(evaluation_data) - 1:
                    file.write(",")

            file.write("\n]")

    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
        parent_output_path: str,
    ):
        output_path = self.__get__evaluation_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        with open(output_path, "w") as file:
            file.write("[")

            for index, evaluation in enumerate(evaluation_data):
                result = EvaluationResultModel()
                result.evaluation_id = evaluation.id

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

                prompt_input = CommitMessageGenerationPromptInputModel()
                prompt_input.diff = diff
                prompt_input.source_code = relevant_source_code

                for generator in generators:
                    generation_result = generator.generate_commit_message(prompt_input)
                    result.generation_results.append(generation_result)

                file.write(f"\n{result.json()}")
                if index < len(evaluation_data) - 1:
                    file.write(",")

            file.write("\n]")
