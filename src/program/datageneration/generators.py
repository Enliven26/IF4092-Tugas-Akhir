import os
from abc import ABC, abstractmethod
from datetime import datetime

from core.chains import IDataGenerationChain


class IDataGenerator(ABC):
    @abstractmethod
    def generate_data(self, diffs: list[str], parent_output_path: str):
        pass


class DataGenerator(IDataGenerator):
    OUTPUT_FILE_NAME = "datageneration.json"

    def __init__(self, chain: IDataGenerationChain):
        super().__init__()
        self.__chain = chain

    def __get_output_path(self, parent_path: str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

        return os.path.join(parent_path, timestamp, self.__class__.OUTPUT_FILE_NAME)

    def __create_folder_if_not_exist(self, path: str):
        directory = os.path.dirname(path)

        if not os.path.exists(directory):
            os.makedirs(directory)

    def generate_data(self, diffs: list[str], parent_output_path: str):
        output_path = self.__get_output_path(parent_output_path)
        self.__create_folder_if_not_exist(output_path)

        with open(output_path, "w") as file:
            file.write("[\n")

            for diff in diffs:
                high_level_context = self.__chain.generate_high_level_context(diff)
                file.write(f'"{high_level_context}"\n')

            file.write("\n]")
