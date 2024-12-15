import os
from abc import ABC, abstractmethod
from datetime import datetime

from core.chains import IDataGenerationChain
from core.enums import DiffVersion
from core.git import IGit
from core.models import DataGenerationPromptInputModel
from core.parsers import ICodeParser, IDiffParser
from datageneration.models import DataGenerationResultModel, ExampleModel


class IDataGenerator(ABC):
    @abstractmethod
    def generate_data(self, diffs: list[str], parent_output_path: str):
        pass


class DataGenerator(IDataGenerator):
    OUTPUT_FILE_NAME = "datageneration.json"

    def __init__(
        self,
        chain: IDataGenerationChain,
        git: IGit,
        diff_parser: IDiffParser,
        code_parser: ICodeParser,
    ):
        super().__init__()
        self.__chain = chain
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

            new_implementations = self.__code_parser.get_methods(
                file_content, file_diff.line_ranges
            )
            implementations.extend(new_implementations)

        return "\n".join(implementations)

    def generate_data(self, examples: list[ExampleModel], parent_output_path: str):
        output_path = self.__get_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        with open(output_path, "w") as file:
            file.write("[")

            for index, example in enumerate(examples):
                current_commit_hash = example.commit_hash
                previous_commit_hash = f"{current_commit_hash}~1"

                diff = self.__git.get_diff(
                    example.repository_path,
                    previous_commit_hash,
                    current_commit_hash,
                    example.included_file_paths,
                )

                relevant_source_code = self.__get_implementations(
                    example.repository_path,
                    previous_commit_hash,
                    current_commit_hash,
                    example.included_file_paths,
                    diff,
                )

                prompt_input = DataGenerationPromptInputModel()
                prompt_input.source_code = relevant_source_code
                prompt_input.github_url = example.repository_url

                high_level_context = self.__chain.generate_high_level_context(
                    prompt_input
                )

                result = DataGenerationResultModel()
                result.diff = diff
                result.source_code = relevant_source_code
                result.high_level_context = high_level_context
                result.commit_message = example.commit_message

                file.write(f"\n{result.json()}")

                if index < len(examples) - 1:
                    file.write(",")

            file.write("\n]")
