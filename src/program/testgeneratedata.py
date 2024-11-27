import json
import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from datageneration import mock_data_generator

DATA_GENERATION_JSON_PATH = os.path.join("data", "datageneration", "diffs.json")
DEFAULT_DATA_GENERATION_OUTPUT_PATH = os.path.join("out", "datageneration.json")


def read_data_generation_json() -> str:
    with open(DATA_GENERATION_JSON_PATH, "r", encoding="utf-8") as file:
        return file.read()


def get_diffs() -> list[str]:
    json_string = read_data_generation_json()

    try:
        diffs = json.loads(json_string)
        if not isinstance(diffs, list):
            raise ValueError("JSON data must be a list of strings.")

        return diffs

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid JSON string for data generation: {e}")


def test_generate(diffs: list[str], output_path: str):
    mock_data_generator.generate_data(diffs, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    output_path = os.getenv(
        EnvironmentKey.DATA_GENERATION_OUTPUT_PATH.value,
        DEFAULT_DATA_GENERATION_OUTPUT_PATH,
    )

    diffs = get_diffs()
    test_generate(diffs, output_path)


if __name__ == "__main__":
    main()
