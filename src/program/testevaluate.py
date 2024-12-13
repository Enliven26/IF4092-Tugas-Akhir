import logging
import os

from dotenv import load_dotenv

from core import mock_commit_message_generation_chain
from evaluation import evaluator
from evaluation.evaluators import CommitMessageGenerator
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "testcommits.json")
EVALUATION_OUTPUT_PATH = os.path.join("out", "test", "evaluation")


def get_evaluation_data() -> list[EvaluationModel]:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return EvaluationModel.from_json(json_string)


def test_evaluate(evaluation_data: list[EvaluationModel], output_path: str):
    generator = CommitMessageGenerator(
        "TestGenerator", mock_commit_message_generation_chain
    )
    generators = [generator]

    evaluator.evaluate(generators, evaluation_data, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    output_path = EVALUATION_OUTPUT_PATH

    evaluation_data = get_evaluation_data()

    test_evaluate(evaluation_data, output_path)


if __name__ == "__main__":
    main()
