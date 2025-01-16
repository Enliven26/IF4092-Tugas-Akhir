import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from runners import example_generator_runner

COMMIT_DATA_JSON_PATH = os.path.join("data", "cmg", "commits.example.json")
DEFAULT_EXAMPLE_GENERATION_OUTPUT_PATH = os.path.join("out", "example")


def main():
    load_dotenv(dotenv_path=".env", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.EXAMPLE_GENERATION_OUTPUT_PATH.value,
        DEFAULT_EXAMPLE_GENERATION_OUTPUT_PATH,
    )

    example_generator_runner.run(
        COMMIT_DATA_JSON_PATH,
        output_path,
        logging.INFO,
    )


if __name__ == "__main__":
    main()
