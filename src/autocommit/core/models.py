import json
import os
from enum import Enum
from typing import get_type_hints, get_args, get_origin, List, Any, Union
from urllib.parse import urlparse

from autocommit.core.enums import DiffVersion


class BaseModel(object):
    @classmethod
    def _from_json_object(cls, name: str, data: Any) -> Any:
        if isinstance(data, dict):
            obj = cls()
            type_hints = get_type_hints(cls)

            for key, value in data.items():
                if key not in type_hints:
                    continue

                expected_type = type_hints[key]
                origin = get_origin(expected_type)

                if origin is Union and type(None) in get_args(expected_type):
                    non_none_args = [arg for arg in get_args(expected_type) if arg is not type(None)]
                    expected_type = non_none_args[0] if non_none_args else Any
                    origin = get_origin(expected_type)

                if isinstance(value, dict) and isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
                    setattr(obj, key, expected_type._from_json_object(key, value))

                elif origin in (list, List):
                    item_type = get_args(expected_type)[0] if get_args(expected_type) else Any
                    if issubclass(item_type, BaseModel):
                        setattr(obj, key, [item_type._from_json_object(key, item) for item in value])
                    else:
                        setattr(obj, key, value)

                elif isinstance(value, expected_type):
                    setattr(obj, key, value)

                else:
                    raise ValueError(
                        f"Invalid data type for '{key}' in '{name}': {type(value)}. Expected {expected_type}."
                    )

            return obj

        elif isinstance(data, list):
            return [cls._from_json_object(name, item) for item in data if isinstance(item, dict)]

        else:
            raise ValueError(
                f"Invalid data type for '{name}': {type(data)}. Expected dict or list."
            )


class FileDiffModel(BaseModel):
    file_path: str = ""
    version: DiffVersion = DiffVersion.NEW
    line_ranges: list[range] = []

class CommitMessageGenerationPromptInputModel(BaseModel):
    diff: str = ""
    source_code: str = ""
    context_file_path = ""
    vector_store_path = ""
    id: str = ""


class DataGenerationPromptInputModel(BaseModel):
    github_url: str = ""
    source_code: str = ""


class JiraContextDocumentRetrieverInputModel(BaseModel):
    query: str = ""
    diff: str = ""


class GetHighLevelContextInputModel(BaseModel):
    source_code: str = ""
    diff: str = ""
    context_file_path = ""
    vector_store_path = ""


class HighLevelContextDiffClassificationInputModel(BaseModel):
    diff: str = ""
    context: str = ""


class CommitDataModel(BaseModel):
    CONTEXT_FILE_NAME = "contexts.txt"
    VECTOR_STORE_FOLDER_NAME = "vector_store"

    commit_hash: str = ""
    included_file_paths: list[str] = []
    repository_path: str = ""
    repository_url: str = ""
    jira_url: str = ""

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
