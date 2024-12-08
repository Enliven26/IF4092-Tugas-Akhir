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
        self.source_code: Optional[str] = None


class DataGenerationPromptInputModel:
    def __init__(self):
        self.diff: str = ""
        self.source_code: Optional[str] = None
