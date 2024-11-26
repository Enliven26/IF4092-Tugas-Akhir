from typing import Optional

class PromptInput:
    def __init__(self):
        self.diff: str = ""
        self.source_code: Optional[str] = None