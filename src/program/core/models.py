from typing import Optional

from core.enums import DiffVersion, ImplementationType


class FileDiffModel:
    def __init__(self):
        self.file_path: str = ""
        self.version: DiffVersion = DiffVersion.NEW
        self.line_ranges: list[range] = []


class ImplementationModel:
    def __init__(self):
        self.modifiers: list[str] = []
        self.name: str = ""
        self.generics: str = ""
        self.constructor: str = ""
        self.supertypes: list[str] = []
        self.constraints: str = ""
        self.body: str = ""
        self.type: ImplementationType = ImplementationType.CLASS

    def __str__(self):
        modifiers = ""
        declaration = ""
        generics = self.generics
        constructor = self.constructor
        supertypes = ""
        constraints = self.constraints
        body = self.body

        if self.modifiers:
            modifiers = f"{' '.join(self.modifiers)} "

        if self.type == ImplementationType.INTERFACE:
            declaration = "interface"
        elif self.type == ImplementationType.CLASS:
            declaration = "class"
        else:
            declaration = "fun interface"

        if self.constructor is not None:
            constructor = str(self.constructor)

        if self.supertypes:
            supertypes = f" : {', '.join(self.supertypes)}"

        if self.constraints:
            constraints = f" {self.constraints!s}"

        return (
            f"{modifiers}{declaration} {self.name}{generics}{constructor}"
            f"{supertypes}{constraints}{body}"
        )


class CommitMessageGenerationPromptInputModel:
    def __init__(self):
        self.diff: str = ""
        self.source_code: Optional[str] = None
