import logging
import os

from dotenv import load_dotenv

from cmg import evaluator
from cmg.evaluators import CommitMessageGenerator
from cmg.models import EvaluationModel
from core import (
    few_shot_high_level_cmg_chain,
    low_level_cmg_chain,
    zero_shot_high_level_cmg_chain,
)
from core.enums import EnvironmentKey

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_CMG_OUTPUT_PATH = os.path.join("out", "evaluation", "cmg")
GENERATORS = [
    CommitMessageGenerator(
        "Zero-Shot High-Level Generator", zero_shot_high_level_cmg_chain
    ),
    CommitMessageGenerator(
        "Few-Shot High-Level Generator", few_shot_high_level_cmg_chain
    ),
    CommitMessageGenerator("Low-Level Generator", low_level_cmg_chain),
]
INCLUDED_GENERATOR_INDEXES = [0, 1, 2]


def get_evaluation_data() -> list[EvaluationModel]:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return EvaluationModel.from_json(json_string)


def test_evaluate(evaluation_data: list[EvaluationModel], output_path: str):
    generators = [GENERATORS[i] for i in INCLUDED_GENERATOR_INDEXES]

    evaluator.evaluate(generators, evaluation_data, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.evaluation", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CMG_OUTPUT_PATH.value, DEFAULT_CMG_OUTPUT_PATH
    )

    evaluation_data = get_evaluation_data()

    test_evaluate(evaluation_data, output_path)


if __name__ == "__main__":
    main()
