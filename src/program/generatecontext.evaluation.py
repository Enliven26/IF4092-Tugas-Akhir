import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from runners import context_generator_runner

COMMIT_DATA_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_DATA_GENERATION_OUTPUT_PATH = os.path.join(
    "out", "evaluation", "contextgeneration"
)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.evaluation", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CONTEXT_GENERATION_OUTPUT_PATH.value,
        DEFAULT_DATA_GENERATION_OUTPUT_PATH,
    )

    context_generator_runner.run(COMMIT_DATA_JSON_PATH, output_path, logging.DEBUG)


if __name__ == "__main__":
    main()
