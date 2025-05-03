import json
import os
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from autocommit.core.enums import DiffVersion


class BaseModel:
    @classmethod
    def _from_json_object(cls, name: str, data: Any) -> Any:
        if isinstance(data, dict):
            return type(
                name, (object,), {k: BaseModel._from_json_object(k, v) for k, v in data.items()}
            )()
        elif isinstance(data, list):
            return [BaseModel._from_json_object(name, item) for item in data]
        else:
            return data


class FileDiffModel(BaseModel):
    def __init__(self):
        self.file_path: str = ""
        self.version: DiffVersion = DiffVersion.NEW
        self.line_ranges: list[range] = []


class CommitMessageGenerationPromptInputModel(BaseModel):
    def __init__(self):
        self.diff: str = ""
        self.source_code: str = ""
        self.context_file_path = ""
        self.vector_store_path = ""
        self.id: str = ""


class DataGenerationPromptInputModel(BaseModel):
    def __init__(self):
        self.github_url: str = ""
        self.source_code: str = ""


class JiraContextDocumentRetrieverInputModel(BaseModel):
    def __init__(self):
        self.query: str = ""
        self.diff: str = ""


class GetHighLevelContextInputModel(BaseModel):
    def __init__(self):
        self.source_code: str = ""
        self.diff: str = ""
        self.context_file_path = ""
        self.vector_store_path = ""


class HighLevelContextDiffClassificationInputModel(BaseModel):
    def __init__(self):
        self.diff: str = ""
        self.context: str = ""


class CommitDataModel(BaseModel):
    CONTEXT_FILE_NAME = "contexts.txt"
    VECTOR_STORE_FOLDER_NAME = "vector_store"

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
        data_list: list[dict[str, Any]] | Any = json.loads(json_string)

        if not isinstance(data_list, list):
            raise ValueError("JSON data must be a list of objects.")

        return cls._from_json_object("CommitDataModel", data_list)
