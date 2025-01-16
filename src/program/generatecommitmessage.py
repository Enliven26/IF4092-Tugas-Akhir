import logging
import os

from cmg import evaluator
from cmg.evaluators import CommitMessageGenerator
from core.models import CommitDataModel
from core.enums import EnvironmentKey
from dotenv import load_dotenv

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "commits.json")
DEFAULT_CMG_OUTPUT_PATH = os.path.join("out", "cmg")


def get_evaluation_data() -> list[CommitDataModel]:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return CommitDataModel.from_json(json_string)


def evaluate(evaluation_data: list[CommitDataModel], output_path: str):
    pass


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CMG_OUTPUT_PATH.value, DEFAULT_CMG_OUTPUT_PATH
    )

    evaluation_data = get_evaluation_data()

    evaluate(evaluation_data, output_path)


if __name__ == "__main__":
    main()
