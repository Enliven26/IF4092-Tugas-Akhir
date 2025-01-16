import logging

from core.models import CommitDataModel
from datapreparation.generators import IContextGenerator
from runners.base import IProgramRunner


class ContextGeneratorRunner(IProgramRunner):
    def __init__(self, context_generator: IContextGenerator):
        self.__context_generator = context_generator

    def run(self, data_path: str, output_path: str, logging_level: int = logging.INFO):
        logging.basicConfig(level=logging_level)

        commits = self._get_commits(data_path)
        self.__context_generator.generate_context(commits, output_path)
