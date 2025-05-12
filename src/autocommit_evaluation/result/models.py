import json
from typing import Any

from autocommit.core.models import BaseModel


class CommitMessageScore(BaseModel):
    rationality_score: int | None = 0
    comprehensiveness_score: int | None = 0
    conciseness_score: int | None = 0
    correctness_score: int | None = 0

    def copy(self) -> "CommitMessageScore":
        new_instance = CommitMessageScore()
        new_instance.rationality_score = self.rationality_score
        new_instance.comprehensiveness_score = self.comprehensiveness_score
        new_instance.conciseness_score = self.conciseness_score
        new_instance.correctness_score = self.correctness_score
        return new_instance


class GeneratorScore(BaseModel):
    generator_id: str = ""
    scores: list[CommitMessageScore] = []

    def copy(self, excluded_indexes: list[int] | None = None) -> "GeneratorScore":
        if excluded_indexes is None:
            excluded_indexes = []

        new_instance = GeneratorScore()
        new_instance.generator_id = self.generator_id
        new_instance.scores = [
            score.copy()
            for idx, score in enumerate(self.scores)
            if idx not in excluded_indexes
        ]
        return new_instance


class TestCaseScore(BaseModel):
    evaluation_id: str = ""
    scores: list[GeneratorScore] = []

    @classmethod
    def from_json(cls, json_string: str) -> list["TestCaseScore"]:
        data_list: list[dict[str, Any]] | Any = json.loads(json_string)

        if not isinstance(data_list, list):
            raise ValueError("JSON data must be a list of objects.")

        return cls._from_json_object("TestCaseScore", data_list)

    def copy(self, excluded_indexes: list[int] | None = None) -> "TestCaseScore":
        if excluded_indexes is None:
            excluded_indexes = []

        new_instance = TestCaseScore()
        new_instance.evaluation_id = self.evaluation_id
        new_instance.scores = [score.copy(excluded_indexes) for score in self.scores]
        return new_instance


class ScoreSummary(BaseModel):
    generator_id: str = ""
    rationality_score: float = 0
    comprehensiveness_score: float = 0
    conciseness_score: float = 0
    correctness_score: float = 0
