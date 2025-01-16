import json
from enum import Enum
from typing import Any, Optional

from core.enums import DiffVersion


class FileDiffModel:
    def __init__(self):
        self.file_path: str = ""
        self.version: DiffVersion = DiffVersion.NEW
        self.line_ranges: list[range] = []


class CommitMessageGenerationPromptInputModel:
    def __init__(self):
        self.diff: str = ""
        self.source_code: str = ""


class DataGenerationPromptInputModel:
    def __init__(self):
        self.github_url: str = ""
        self.source_code: str = ""


class DiffContextDocumentRetrieverInputModel:
    def __init__(self):
        self.query: str = ""
        self.diff: str = ""


class GetHighLevelContextInputModel:
    def __init__(self):
        self.source_code: str = ""
        self.diff: str = ""


class CommitDataModel:
    class __JsonKey(Enum):
        ID = "id"
        PREVIOUS_COMMIT_HASH = "previos_commit_hash"
        CURRENT_COMMIT_HASH = "current_commit_hash"
        INCLUDED_FILE_PATHS = "included_file_paths"
        REPOSITORY_PATH = "repository_path"
        REPOSITORY_URL = "repository_url"

    def __init__(self):
        self.id: str = ""
        self.previous_commit_hash: Optional[str] = None
        self.current_commit_hash: str = ""
        self.included_file_paths: list[str] = []
        self.repository_path: str = ""
        self.repository_url: str = ""

    @classmethod
    def from_json(cls, json_string: str) -> list["CommitDataModel"]:
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
                    cls.__JsonKey.PREVIOUS_COMMIT_HASH.value, ""
                )
                instance.current_commit_hash = data.get(
                    cls.__JsonKey.CURRENT_COMMIT_HASH.value, ""
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
