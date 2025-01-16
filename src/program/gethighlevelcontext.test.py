import logging
import os

from cmg import evaluator
from cmg.models import CommitDataModel
from core import zero_shot_high_level_cmg_chain
from core.enums import EnvironmentKey
from dotenv import load_dotenv

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH = os.path.join("out", "test", "highlevelcontext")
SAMPLE_EVALUATION_ID = "ETC003"


def get_evaluation_sample() -> CommitDataModel:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        evaluation_data = CommitDataModel.from_json(json_string)

        for evaluation in evaluation_data:
            if evaluation.id == SAMPLE_EVALUATION_ID:
                return evaluation

        raise ValueError(f"Evaluation with ID {SAMPLE_EVALUATION_ID} not found.")


def test_get_high_level_context(evaluation: CommitDataModel, output_path: str):
    evaluator.get_high_level_contexts(
        zero_shot_high_level_cmg_chain, evaluation, output_path
    )


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    evaluation_sample = get_evaluation_sample()
    output_path = os.getenv(
        EnvironmentKey.HIGH_LEVEL_CONTEXT_OUTPUT_PATH.value,
        DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH,
    )

    test_get_high_level_context([evaluation_sample], output_path)


if __name__ == "__main__":
    main()
