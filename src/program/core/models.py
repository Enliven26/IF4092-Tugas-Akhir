from typing import Optional

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

class HighLevelContextDocumentRetrieverInputModel:
    def __init__(self):
        self.query: str = ""
        self.diff: str = ""
