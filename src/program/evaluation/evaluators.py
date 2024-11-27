from abc import ABC, abstractmethod

from core.chains import ICommitMessageGenerationChain
from core.enums import DiffVersion
from core.git import IGit
from core.models import CommitMessageGenerationPromptInput, ImplementationModel
from core.parsers import ICodeParser, IDiffParser
from evaluation.models import (
    EvaluationModel,
    EvaluationResultModel,
    GenerationResultModel,
)

import os
from datetime import datetime

class ICommitMessageGenerator(ABC):
    @abstractmethod
    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInput
    ) -> GenerationResultModel:
        pass


class CommitMessageGenerator(ICommitMessageGenerator):
    def __init__(self, id: str, chain: ICommitMessageGenerationChain):
        super().__init__()
        self.id = id
        self.__chain = chain

    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInput
    ) -> GenerationResultModel:
        commit_message = self.__chain.generate_commit_message(prompt_input)
        result = GenerationResultModel()
        result.generator_id = self.id
        result.commit_message = commit_message

        return result


class IEvaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
        parent_output_path: str
    ):
        pass


class Evaluator(IEvaluator):
    OUTPUT_FILE_NAME = "evaluation.json"

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
    ) -> list[ImplementationModel]:
        commit_map = {
            DiffVersion.OLD: previous_commit_hash,
            DiffVersion.NEW: current_commit_hash,
        }

        file_diffs = self.__diff_parser.get_diff_lines(diff, included_file_paths)

        implementations: list[ImplementationModel] = []

        for file_diff in file_diffs:
            file_content = self.__git.get_file_content(
                source_repo_path, commit_map[file_diff.version], file_diff.file_path
            )

            new_implementations = self.__code_parser.get_methods(
                file_content, file_diff.line_ranges
            )
            implementations.extend(new_implementations)

        return implementations

    def __get_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(parent_path, timestamp, self.__class__.OUTPUT_FILE_NAME)
    
    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def evaluate(
        self,
        source_repo_path: str,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
        parent_output_path: str
    ):
        output_path = self.__get_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)
        
        with open(output_path, "w") as file:
            file.write("[\n")

            for evaluation in evaluation_data:
                result = EvaluationResultModel()
                result.evaluation_id = evaluation.id

                current_commit_hash = evaluation.current_commit_hash
                previous_commit_hash = (
                    evaluation.previous_commit_hash or f"{current_commit_hash}~1"
                )

                diff = self.__git.get_diff(
                    source_repo_path,
                    previous_commit_hash,
                    current_commit_hash,
                    evaluation.included_file_paths,
                )

                implementations = self.__get_implementations(
                    source_repo_path,
                    previous_commit_hash,
                    current_commit_hash,
                    evaluation.included_file_paths,
                    diff,
                )

                relevant_source_code = "\n".join(map(str, implementations))

                prompt_input = CommitMessageGenerationPromptInput()
                prompt_input.diff = diff
                prompt_input.source_code = relevant_source_code

                for generator in generators:
                    generation_result = generator.generate_commit_message(prompt_input)
                    result.generation_results.append(generation_result)

                file.write(f"{result.json()},\n")

            file.write("\n]")

