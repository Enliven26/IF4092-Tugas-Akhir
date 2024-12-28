import logging
import os

from dotenv import load_dotenv

from cmg import evaluator
from cmg.models import EvaluationModel
from core import zero_shot_high_level_cmg_chain
from core.enums import EnvironmentKey

EVALUATION_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH = os.path.join(
    "out", "test", "diffclassification"
)
SAMPLE_EVALUATION_ID = "ETC003"


def get_evaluation_sample() -> EvaluationModel:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        evaluation_data = EvaluationModel.from_json(json_string)

        for evaluation in evaluation_data:
            if evaluation.id == SAMPLE_EVALUATION_ID:
                return evaluation

        raise ValueError(f"Evaluation with ID {SAMPLE_EVALUATION_ID} not found.")


def test_classify_diffs(evaluation: EvaluationModel, output_path: str):
    evaluator.classify_diffs(zero_shot_high_level_cmg_chain, evaluation, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    evaluation_sample = get_evaluation_sample()
    output_path = os.getenv(
        EnvironmentKey.DIFF_CLASSIFICATION_OUTPUT_PATH.value,
        DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH,
    )

    test_classify_diffs([evaluation_sample], output_path)


if __name__ == "__main__":
    main()
