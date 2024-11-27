import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from evaluation.models import EvaluationModel

EVALUATION_JSON_PATH = os.path.join("data", "evaluation", "commits.json")


def read_evaluation_json():
    with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as file:
        return file.read()


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    source_repo_path = os.getenv(EnvironmentKey.SOURCE_REPO_PATH.value)

    if (source_repo_path is None):
        logging.warning("SOURCE_REPO_PATH is not set.")
        return
    
    

    evaluation_json_string = read_evaluation_json()
    evaluation_data = EvaluationModel.from_json(evaluation_json_string)
    pass


if __name__ == "__main__":
    main()
