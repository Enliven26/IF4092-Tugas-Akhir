import json
from enum import Enum
from typing import Any, Optional


class ExampleModel:
    class __JsonKey(Enum):
        COMMIT_HASH = "commit_hash"
        COMMIT_MESSAGE = "commit_message"
        INCLUDED_FILE_PATHS = "included_file_paths"
        REPOSITORY_PATH = "repository_path"
        REPOSITORY_URL = "repository_url"

    def __init__(self):
        self.commit_hash: Optional[str] = None
        self.commit_message: str = ""
        self.included_file_paths: list[str] = []
        self.repository_path: str = ""
        self.repository_url: str = ""

    @classmethod
    def from_json(cls, json_string: str) -> list["ExampleModel"]:
        try:
            data_list = json.loads(json_string)
            if not isinstance(data_list, list):
                raise ValueError("JSON data must be a list of objects.")

            data_list: list[dict[str, Any]] = data_list

            instances = []
            for data in data_list:
                instance = cls()
                instance.commit_hash = data.get(cls.__JsonKey.COMMIT_HASH.value, "")
                instance.commit_message = data.get(
                    cls.__JsonKey.COMMIT_MESSAGE.value, ""
                )
                instance.included_file_paths = data.get(
                    cls.__JsonKey.INCLUDED_FILE_PATHS.value, []
                )

                instance.repository_path = data.get(
                    cls.__JsonKey.REPOSITORY_PATH.value, ""
                )

                instance.repository_url = data.get(
                    cls.__JsonKey.REPOSITORY_URL.value, ""
                )

                instances.append(instance)

            return instances

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON string for EvaluationModel list: {e}")


class DataGenerationResultModel:
    def __init__(self):
        self.diff = ""
        self.source_code = ""
        self.high_level_context = ""
        self.commit_message = ""
