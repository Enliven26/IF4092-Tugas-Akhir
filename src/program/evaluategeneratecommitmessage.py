import logging
import os

from dotenv import load_dotenv

from cmg import evaluator
from cmg.evaluators import CommitMessageGenerator
from cmg.models import EvaluationModel
from core import high_level_cmg_chain
from core.enums import EnvironmentKey

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_CMG_OUTPUT_PATH = os.path.join("out", "test", "cmg")


def get_evaluation_data() -> list[EvaluationModel]:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return EvaluationModel.from_json(json_string)


def test_evaluate(evaluation_data: list[EvaluationModel], output_path: str):
    generator = CommitMessageGenerator("TestGenerator", high_level_cmg_chain)
    generators = [generator]

    evaluator.evaluate(generators, evaluation_data, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CMG_OUTPUT_PATH.value, DEFAULT_CMG_OUTPUT_PATH
    )

    evaluation_data = get_evaluation_data()

    test_evaluate(evaluation_data, output_path)


if __name__ == "__main__":
    main()
