import logging
import os

from dotenv import load_dotenv

from core import mock_commit_message_generation_chain
from core.enums import EnvironmentKey
from evaluation import evaluator
from evaluation.evaluators import CommitMessageGenerator
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "commits.json")
DEFAULT_EVALUATION_OUTPUT_PATH = os.path.join("out", "evaluation.json")


def read_evaluation_json():
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        return file.read()


def test_evaluate(
    evaluation_data: list[EvaluationModel], source_repo_path: str, output_path: str
):
    generator = CommitMessageGenerator(
        "TestGenerator", mock_commit_message_generation_chain
    )
    generators = [generator]

    evaluator.evaluate(source_repo_path, generators, evaluation_data, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    source_repo_path = os.getenv(EnvironmentKey.SOURCE_REPO_PATH.value)

    if source_repo_path is None:
        logging.warning("SOURCE_REPO_PATH is not set.")
        return

    output_path = os.getenv(
        EnvironmentKey.EVALUATION_OUTPUT_PATH.value, DEFAULT_EVALUATION_OUTPUT_PATH
    )

    evaluation_json_string = read_evaluation_json()
    evaluation_data = EvaluationModel.from_json(evaluation_json_string)

    test_evaluate(evaluation_data, source_repo_path, output_path)


if __name__ == "__main__":
    main()
