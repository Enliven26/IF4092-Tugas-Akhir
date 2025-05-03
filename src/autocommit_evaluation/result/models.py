import json
from typing import Any

from autocommit.core.models import BaseModel


class CommitMessageScore(BaseModel):
    def __init__(self):
        self.rationality_score: int | None = 0
        self.comprehensiveness_score: int | None = 0
        self.conciseness_score: int | None = 0
        self.correctness_score: int | None = 0


class GeneratorScore(BaseModel):
    def __init__(self):
        self.generator_id: str = ""
        self.scores: list[CommitMessageScore] = []


class TestCaseScore(BaseModel):
    def __init__(self):
        self.evaluation_id: str = ""
        self.scores: list[GeneratorScore] = []

    @classmethod
    def from_json(cls, json_string: str) -> list["TestCaseScore"]:
        data_list: list[dict[str, Any]] | Any = json.loads(json_string)

        if not isinstance(data_list, list):
            raise ValueError("JSON data must be a list of objects.")

        return cls._from_json_object("TestCaseScore", data_list)


class ScoreSummary(BaseModel):
    def __init__(self):
        self.generator_id: str = ""
        self.rationality_score: float = 0
        self.comprehensiveness_score: float = 0
        self.conciseness_score: float = 0
        self.correctness_score: float = 0
