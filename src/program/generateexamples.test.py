import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from datapreparation import context_generator
from datapreparation.models import ExampleModel

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
    context_generator.generate_context(examples, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CONTEXT_GENERATION_OUTPUT_PATH.value,
        DEFAULT_DATA_GENERATION_OUTPUT_PATH,
    )

    example = get_example_sample()
    test_generate([example], output_path)


if __name__ == "__main__":
    main()
