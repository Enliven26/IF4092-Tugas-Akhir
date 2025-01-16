import logging
import os

from dotenv import load_dotenv

from cmg.evaluators import CommitMessageGenerator
from core import (
    few_shot_high_level_cmg_chain,
    low_level_cmg_chain,
    zero_shot_high_level_cmg_chain,
)
from core.enums import EnvironmentKey
from runners import cmg_runner

COMMIT_DATA_JSON_PATH = os.path.join("data", "cmg", "commits.evaluation.json")
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
INCLUDED_GENERATOR_INDEXES = [0, 1]


def evaluate(output_path: str):
    generators = [GENERATORS[i] for i in INCLUDED_GENERATOR_INDEXES]
    cmg_runner.run(generators, COMMIT_DATA_JSON_PATH, output_path, logging.DEBUG)


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv(dotenv_path=".env.evaluation", verbose=True, override=True)

    output_path = os.getenv(
        EnvironmentKey.CMG_OUTPUT_PATH.value, DEFAULT_CMG_OUTPUT_PATH
    )

    evaluate(output_path)


if __name__ == "__main__":
    main()
