from abc import ABC, abstractmethod
from typing import Optional

from kopyt import Parser, node


class DiffLineModel:
    def __init__(self):
        self.start_line: int = 0
        self.end_line: int = 0


class ImplementationModel:
    def __init__(self):
        self.parent_class_declaration: Optional[str] = None
        self.source: str = ""


class IDiffParser(ABC):
    @abstractmethod
    def get_diff_lines(self, commit: Optional[str] = None) -> list[DiffLineModel]:
        pass


class ICodeParser(ABC):
    @abstractmethod
    def get_methods(
        self, source_code: str, line_ranges: list[range]
    ) -> list[ImplementationModel]:
        pass


class CodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def get_methods(
        self, source_code: str, line_ranges: list[range]
    ) -> list[ImplementationModel]:
        parser = Parser(source_code)
        parser_result = parser.parse()

        result: list[ImplementationModel] = []

        for declaration in parser_result.declarations:
            if isinstance(declaration, node.ClassDeclaration):
                for member in declaration.body.members:
                    start_line = member.position.line
                    end_line = start_line + len(str(member)) - 1
                    # TODO check if we should include

            else:
                # TODO: treat this as method inside class
                pass
