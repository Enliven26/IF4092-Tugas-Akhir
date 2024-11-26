import json
from enum import Enum
from typing import Any, Optional


class EvaluationModel:
    class __JsonKey(Enum):
        ID = "id"
        PREVIOUS_COMMIT_HASH = "previousCommitHash"
        CURRENT_COMMIT_HASH = "currentCommitHash"
        INCLUDED_FILE_PATHS = "includedFilePaths"

    def __init__(self):
        self.id: str = ""
        self.previous_commit_hash: Optional[str] = None
        self.current_commit_hash: str = ""
        self.included_file_paths: list[str] = []

    @classmethod
    def from_json(cls, json_string: str) -> list["EvaluationModel"]:
        try:
            data_list = json.loads(json_string)
            if not isinstance(data_list, list):
                raise ValueError("JSON data must be a list of objects.")

            data_list: list[dict[str, Any]] = data_list

            instances = []
            for data in data_list:
                instance = cls()
                instance.id = data.get(cls.__JsonKey.ID.value, "")
                instance.previous_commit_hash = data.get(
                    cls.__JsonKey.PREVIOUS_COMMIT_HASH.value
                )
                instance.current_commit_hash = data.get(
                    cls.__JsonKey.CURRENT_COMMIT_HASH.value, ""
                )
                instance.included_file_paths = data.get(
                    cls.__JsonKey.INCLUDED_FILE_PATHS.value, []
                )

                instances.append(instance)

            return instances

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON string for EvaluationModel list: {e}")


class GenerationResultModel:
    def __init__(self):
        self.generator_id: str = ""
        self.commit_message: str = ""


class EvaluationResultModel:
    def __init__(self):
        self.evaluation_id: str = ""
        self.generation_results: list[GenerationResultModel] = []
