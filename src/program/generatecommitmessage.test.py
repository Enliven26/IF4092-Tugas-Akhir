import logging
import os

from cmg import evaluator
from cmg.evaluators import CommitMessageGenerator
from cmg.models import CommitDataModel
from core import (
    few_shot_high_level_cmg_chain,
    low_level_cmg_chain,
    zero_shot_high_level_cmg_chain,
)
from core.enums import EnvironmentKey
from dotenv import load_dotenv

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_CMG_OUTPUT_PATH = os.path.join("out", "test", "cmg")
SAMPLE_EVALUATION_ID = "ETC003"
GENERATORS = [
    CommitMessageGenerator(
        "Zero-Shot High-Level Generator", zero_shot_high_level_cmg_chain
    ),
    CommitMessageGenerator(
        "Few-Shot High-Level Generator", few_shot_high_level_cmg_chain
    ),
    CommitMessageGenerator("Low-Level Generator", low_level_cmg_chain),
]
INCLUDED_GENERATOR_INDEXES = [2]


def get_evaluation_sample() -> CommitDataModel:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        evaluation_data = CommitDataModel.from_json(json_string)

        for evaluation in evaluation_data:
            if evaluation.id == SAMPLE_EVALUATION_ID:
                return evaluation

        raise ValueError(f"Evaluation with ID {SAMPLE_EVALUATION_ID} not found.")


def test_evaluate(evaluation_data: list[CommitDataModel], output_path: str):
    generators = [GENERATORS[i] for i in INCLUDED_GENERATOR_INDEXES]

    evaluator.evaluate(generators, evaluation_data, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CMG_OUTPUT_PATH.value, DEFAULT_CMG_OUTPUT_PATH
    )

    evaluation_sample = get_evaluation_sample()

    test_evaluate([evaluation_sample], output_path)


if __name__ == "__main__":
    main()
