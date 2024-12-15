import os

from dotenv import load_dotenv

from core import high_level_cmg_chain
from core.enums import EnvironmentKey
from evaluation import evaluator
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "commits.json")
DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH = os.path.join("out", "test", "highlevelcontext")
SAMPLE_EVALUATION_ID = "TC001"


def get_evaluation_sample() -> EvaluationModel:
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        evaluation_data = EvaluationModel.from_json(json_string)

        for evaluation in evaluation_data:
            if evaluation.id == SAMPLE_EVALUATION_ID:
                return evaluation

        raise ValueError(f"Evaluation with ID {SAMPLE_EVALUATION_ID} not found.")


def test_get_high_level_context(
    evaluation: EvaluationModel, output_path: str
):
    evaluator.get_high_level_context(high_level_cmg_chain, evaluation, output_path)


def main():
    load_dotenv(dotenv_path=".env.test", verbose=True, override=True)

    evaluation_sample = get_evaluation_sample()
    output_path = os.getenv(
        EnvironmentKey.HIGH_LEVEL_CONTEXT_OUTPUT_PATH.value,
        DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH,
    )

    test_get_high_level_context(evaluation_sample, output_path)


if __name__ == "__main__":
    main()
