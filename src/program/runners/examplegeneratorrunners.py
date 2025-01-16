import logging

from datapreparation.generators import IExampleGenerator
from runners.base import IProgramRunner


class ExampleGeneratorRunner(IProgramRunner):
    def __init__(self, generator: IExampleGenerator):
        self.__generator = generator

    def run(
        self,
        data_path: str,
        output_path: str,
        logging_level: int = logging.INFO,
    ):
        logging.basicConfig(level=logging_level)

        commits = self._get_commits(data_path)
        self.__generator.generate_examples(
            commits, output_path
        )
