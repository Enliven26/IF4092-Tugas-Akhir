import logging
import os

from dotenv import load_dotenv

from cmg import evaluator
from core import zero_shot_high_level_cmg_chain
from core.enums import EnvironmentKey
from core.models import CommitDataModel

COMMIT_DATA_JSON_PATH = os.path.join("data", "cmg", "evaluationcommits.json")
DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH = os.path.join(
    "out", "evaluation", "diffclassification"
)


def get_evaluation_data() -> list[CommitDataModel]:
    with open(COMMIT_DATA_JSON_PATH, "r", encoding="utf-8") as file:
        json_string = file.read()

        return CommitDataModel.from_json(json_string)


def test_classify_diffs(evaluation: CommitDataModel, output_path: str):
    evaluator.classify_diffs(zero_shot_high_level_cmg_chain, evaluation, output_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.evaluation", verbose=True, override=True)

    evaluation_data = get_evaluation_data()
    output_path = os.getenv(
        EnvironmentKey.DIFF_CLASSIFICATION_OUTPUT_PATH.value,
        DEFAULT_HIGH_LEVEL_CONTEXT_OUTPUT_PATH,
    )

    test_classify_diffs(evaluation_data, output_path)


if __name__ == "__main__":
    main()
