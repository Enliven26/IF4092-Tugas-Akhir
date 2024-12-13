import os

from dotenv import load_dotenv

from core import high_level_cmg_chain
from evaluation import evaluator
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "commits.json")
EVALUATION_OUTPUT_PATH = os.path.join("out", "highlevelcontext")
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
    evaluation_data: list[EvaluationModel], output_path: str
):
    evaluator.get_high_level_context(high_level_cmg_chain, evaluation_data, output_path)


def main():
    load_dotenv()
    evaluation_sample = get_evaluation_sample()
    test_get_high_level_context([evaluation_sample], EVALUATION_OUTPUT_PATH)


if __name__ == "__main__":
    main()
