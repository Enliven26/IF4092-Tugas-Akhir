import logging

from cmg.evaluators import Evaluator
from core import zero_shot_high_level_cmg_chain
from runners.base import IProgramRunner


class GetHighLevelContextRunner(IProgramRunner):
    def __init__(self, evaluator: Evaluator):
        self.__evaluator = evaluator

    def run(
        self,
        data_path: str,
        output_path: str,
        logging_level: int = logging.INFO,
    ):
        logging.basicConfig(level=logging_level)

        commits = self._get_commits(data_path)
        self.__evaluator.get_high_level_contexts(
            zero_shot_high_level_cmg_chain, commits, output_path
        )
