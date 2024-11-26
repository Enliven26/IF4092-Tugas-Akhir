from abc import ABC, abstractmethod

from core.enums import DiffVersion
from core.git import IGit
from core.models import ImplementationModel
from core.parsers import ICodeParser, IDiffParser
from evaluation.models import (
    EvaluationModel,
    EvaluationResultModel,
    GenerationResultModel,
)


class ICommitMessageGenerator(ABC):
    @abstractmethod
    def generate_commit_message(self, diff: str) -> GenerationResultModel:
        pass


class IEvaluator(ABC):
    @abstractmethod
    def evaluate(
        self,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
    ) -> list[EvaluationResultModel]:
        pass


class Evaluator(IEvaluator):
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

    def evaluate(
        self,
        source_repo_path: str,
        generators: list[ICommitMessageGenerator],
        evaluation_data: list[EvaluationModel],
    ) -> list[EvaluationResultModel]:
        results: list[EvaluationResultModel] = []

        for evaluation in evaluation_data:
            result = EvaluationResultModel()
            result.evaluation_id = evaluation.id

            # TODO: remove below logic to chain that use implementation context
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

            # TODO

        return result
