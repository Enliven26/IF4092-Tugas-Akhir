import logging
import os

from core.enums import EnvironmentKey
from datageneration import data_generator
from datageneration.models import ExampleModel
from dotenv import load_dotenv

DATA_GENERATION_JSON_PATH = os.path.join(
    "data", "datageneration", "evaluationexamples.json"
)
DEFAULT_DATA_GENERATION_OUTPUT_PATH = os.path.join("out", "test", "datageneration")
EXAMPLE_INDEX = 0


def get_example_sample() -> ExampleModel:
    with open(DATA_GENERATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        examples = ExampleModel.from_json(json_string)

        return examples[EXAMPLE_INDEX]


def test_generate(examples: list[ExampleModel], output_path: str):
    data_generator.generate_data(examples, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.DATA_GENERATION_OUTPUT_PATH.value,
        DEFAULT_DATA_GENERATION_OUTPUT_PATH,
    )

    example = get_example_sample()
    test_generate([example], output_path)


if __name__ == "__main__":
    main()
