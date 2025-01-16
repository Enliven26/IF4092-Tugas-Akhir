import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from datapreparation import context_generator
from datapreparation.models import ExampleModel

DATA_GENERATION_JSON_PATH = os.path.join("data", "datageneration", "examples.json")
DEFAULT_DATA_GENERATION_OUTPUT_PATH = os.path.join("out", "datageneration")


def get_examples() -> list[ExampleModel]:
    with open(DATA_GENERATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return ExampleModel.from_json(json_string)


def generate(examples: list[ExampleModel], output_path: str):
    context_generator.generate_context(examples, output_path)


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CONTEXT_GENERATION_OUTPUT_PATH.value,
        DEFAULT_DATA_GENERATION_OUTPUT_PATH,
    )

    examples = get_examples()

    generate(examples, output_path)


if __name__ == "__main__":
    main()
