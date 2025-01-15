from abc import ABC, abstractmethod


class ICodeParser(ABC):
    @abstractmethod
    def get_declarations(self, source_code: str, line_ranges: list[range]) -> list[str]:
        pass
