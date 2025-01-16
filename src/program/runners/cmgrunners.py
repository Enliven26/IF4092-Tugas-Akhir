import logging

from cmg.evaluators import ICommitMessageGenerator, IEvaluator
from core.models import CommitDataModel
from runners.base import IProgramRunner


class CmgRunner(IProgramRunner):
    def __init__(self, evaluator: IEvaluator):
        self.__evaluator = evaluator

    def __get_commits(self, path: str) -> list[CommitDataModel]:
        with open(path, "r", encoding="utf-8") as file:
            json_string = file.read()

        return CommitDataModel.from_json(json_string)

    def run(
        self,
        generators: list[ICommitMessageGenerator],
        data_path: str,
        output_path: str,
        logging_level: int = logging.INFO,
    ):
        logging.basicConfig(level=logging_level)

        commits = self.__get_commits(data_path)
        return self.__evaluator.evaluate(generators, commits, output_path)
