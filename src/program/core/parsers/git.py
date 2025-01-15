from abc import ABC, abstractmethod

from core.enums import DiffVersion
from core.models import FileDiffModel
from diff_parser import Diff, DiffBlock


class IDiffParser(ABC):
    @abstractmethod
    def get_diff_lines(
        self, diff: str, included_file_paths: set[str]
    ) -> list[FileDiffModel]:
        pass


class DiffParser(IDiffParser):
    def __get_range(self, block: DiffBlock, version: DiffVersion) -> range:
        if version == DiffVersion.OLD:
            return range(
                block.original_line_start,
                block.original_line_start + block.original_line_count - 1,
            )

        return range(
            block.modified_line_start,
            block.modified_line_start + block.modified_line_count - 1,
        )

    def get_diff_lines(
        self, diff: str, included_file_paths: list[str]
    ) -> list[FileDiffModel]:
        memo: dict[tuple[str, int], FileDiffModel] = {}
        parsed_diff = Diff(diff)
        file_paths = set(included_file_paths)

        for block in parsed_diff:
            block.old_filepath = block.old_filepath.lstrip("/")
            block.new_filepath = block.new_filepath.lstrip("/")

        for block in parsed_diff:
            if block.type != "new" and block.old_filepath in file_paths:
                model = memo.get((block.old_filepath, DiffVersion.OLD.value))

                if model is None:
                    model = FileDiffModel()
                    model.file_path = block.old_filepath
                    model.version = DiffVersion.OLD
                    model.line_ranges = []

                    memo[(model.file_path, model.version.value)] = model

                line_range = self.__get_range(block, DiffVersion.OLD)
                model.line_ranges.append(line_range)

            if block.type != "deleted" and block.new_filepath in file_paths:
                model = memo.get((block.new_filepath, DiffVersion.NEW.value))

                if model is None:
                    model = FileDiffModel()
                    model.file_path = block.new_filepath
                    model.version = DiffVersion.NEW
                    model.line_ranges = []

                    memo[(model.file_path, model.version.value)] = model

                line_range = self.__get_range(block, DiffVersion.NEW)
                model.line_ranges.append(line_range)

        return list(memo.values())
