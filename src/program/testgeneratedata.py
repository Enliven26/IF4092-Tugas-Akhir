import logging
import os

from dotenv import load_dotenv

from datageneration import mock_data_generator
from datageneration.models import ExampleModel

DATA_GENERATION_JSON_PATH = os.path.join("data", "datageneration", "testexamples.json")
DATA_GENERATION_OUTPUT_PATH = os.path.join("out", "test", "datageneration")


def read_data_generation_json() -> str:
    with open(DATA_GENERATION_JSON_PATH, "r", encoding="utf-8") as file:
        return file.read()


def get_examples() -> list[str]:
    json_string = read_data_generation_json()
    return ExampleModel.from_json(json_string)


def test_generate(examples: list[ExampleModel], output_path: str):
    mock_data_generator.generate_data(examples, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    output_path = DATA_GENERATION_OUTPUT_PATH

    examples = get_examples()
    test_generate(examples, output_path)


if __name__ == "__main__":
    main()
