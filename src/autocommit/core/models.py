import json
import os
from enum import Enum
from typing import Any
from urllib.parse import urlparse

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
        self.context_file_path = ""
        self.vector_store_path = ""


class DataGenerationPromptInputModel:
    def __init__(self):
        self.github_url: str = ""
        self.source_code: str = ""


class JiraContextDocumentRetrieverInputModel:
    def __init__(self):
        self.query: str = ""
        self.diff: str = ""


class GetHighLevelContextInputModel:
    def __init__(self):
        self.source_code: str = ""
        self.diff: str = ""
        self.context_file_path = ""
        self.vector_store_path = ""

class HighLevelContextDiffClassificationInputModel:
    def __init__(self):
        self.diff: str = ""
        self.context: str = ""

class CommitDataModel:
    CONTEXT_FILE_NAME = "contexts.txt"
    VECTOR_STORE_FOLDER_NAME = "vector_store"

    class __JsonKey(Enum):
        ID = "id"
        COMMIT_HASH = "commit_hash"
        INCLUDED_FILE_PATHS = "included_file_paths"
        REPOSITORY_PATH = "repository_path"
        REPOSITORY_URL = "repository_url"
        JIRA_URL = "jira_url"

    def __init__(self):
        self.id: str = ""
        self.commit_hash: str = ""
        self.included_file_paths: list[str] = []
        self.repository_path: str = ""
        self.repository_url: str = ""
        self.jira_url: str = ""

    def get_context_relative_path(self) -> str:
        parsed_url = urlparse(self.repository_url)
        path = parsed_url.path.lstrip("/")
        return os.path.normpath(path)

    def get_vector_store_relative_path(self) -> str:
        return os.path.join(
            self.get_context_relative_path(),
            self.VECTOR_STORE_FOLDER_NAME,
        )

    def get_context_file_relative_path(self) -> str:
        return os.path.join(
            self.get_context_relative_path(),
            self.CONTEXT_FILE_NAME,
        )

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
                instance.commit_hash = data.get(cls.__JsonKey.COMMIT_HASH.value, "")
                instance.included_file_paths = data.get(
                    cls.__JsonKey.INCLUDED_FILE_PATHS.value, []
                )

                instance.repository_path = data.get(
                    cls.__JsonKey.REPOSITORY_PATH.value, ""
                )
                instance.repository_url = data.get(
                    cls.__JsonKey.REPOSITORY_URL.value, ""
                )
                instance.jira_url = data.get(cls.__JsonKey.JIRA_URL.value, "")

                instances.append(instance)

            return instances

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON string for EvaluationModel list: {e}")
