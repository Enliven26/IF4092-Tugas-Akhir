import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from evaluation import evaluator
from evaluation.evaluators import CommitMessageGenerator
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "commits.json")
DEFAULT_EVALUATION_OUTPUT_PATH = os.path.join("out", "evaluation.json")


def get_evaluation_data() -> list[EvaluationModel]:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return EvaluationModel.from_json(json_string)


def evaluate(evaluation_data: list[EvaluationModel], output_path: str):
    pass


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.EVALUATION_OUTPUT_PATH.value, DEFAULT_EVALUATION_OUTPUT_PATH
    )

    evaluation_data = get_evaluation_data()

    evaluate(evaluation_data, output_path)


if __name__ == "__main__":
    main()
