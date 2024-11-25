from abc import ABC, abstractmethod
from textwrap import indent

from kopyt import Parser, node

from core.enums import DiffVersion, ImplementationType
from diff_parser import Diff, DiffBlock


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


class ICodeParser(ABC):
    @abstractmethod
    def get_methods(
        self, source_code: str, line_ranges: list[range]
    ) -> list[ImplementationModel]:
        pass


class CodeParser(ICodeParser):
    class __ClassBodyModel:
        __DEFAULT_INDENTATION_PREFIX = "    "

        def __init__(self):
            self.members: list[str] = []

        def __str__(self):
            class_body_string = "\n\n".join(
                indent(
                    str(member),
                    self.__class__.__DEFAULT_INDENTATION_PREFIX,
                )
                for member in self.members
            )
            return f"{{\n{class_body_string}\n}}"

    def __init__(self):
        super().__init__()

    def __calculate_end_line(self, start_line: int, source_code: str):
        line_count = len(source_code.splitlines())
        return start_line + line_count - 1

    def __is_implementation_included(
        self,
        line_ranges: list[range],
        implementation_start_line: str,
        implementation_end_line: str,
    ):

        for line_range in line_ranges:
            if not (
                implementation_start_line > line_range.stop
                or implementation_end_line < line_range.start
            ):
                return True

        return False

    def __set_parent_data(
        self, model: ImplementationModel, declaration: node.ClassDeclaration
    ):
        model.modifiers = map(str, declaration.modifiers)
        model.name = declaration.name
        model.generics = str(declaration.generics) if declaration.generics else ""
        model.constructor = (
            "" if declaration.constructor is None else str(declaration.constructor)
        )
        model.supertypes = map(str, declaration.supertypes)
        model.constraints = (
            str(declaration.constraints) if declaration.constraints else ""
        )

        if isinstance(declaration, node.InterfaceDeclaration):
            model.type = ImplementationType.INTERFACE
        elif isinstance(declaration, node.FunctionalInterfaceDeclaration):
            declaration = ImplementationType.FUNCTIONAL_INTERFACE
        else:
            declaration = ImplementationType.CLASS

    def get_methods(
        self, source_code: str, line_ranges: list[range]
    ) -> list[ImplementationModel]:
        parser = Parser(source_code)
        parser_result = parser.parse()

        result: list[ImplementationModel] = []

        for declaration in parser_result.declarations:
            if isinstance(declaration, node.ClassDeclaration):
                parent_string = str(declaration)  # TODO: fix this since this is not the real implementation, ignoring comments and empty lines

                print(parent_string)

                parent_start_line = declaration.position.line
                parent_end_line = self.__calculate_end_line(
                    parent_start_line, parent_string
                )

                is_parent_included = self.__is_implementation_included(
                    line_ranges, parent_start_line, parent_end_line
                )

                if not is_parent_included:
                    continue

                model = ImplementationModel()
                self.__set_parent_data(model, declaration)

                if isinstance(declaration.body, node.EnumClassBody):
                    model.body = str(declaration.body)

                else:
                    body = self.__class__.__ClassBodyModel()

                    for member in declaration.body.members:
                        member_string = str(member)  # TODO: fix this since this is not the real implementation, ignoring comments and empty lines

                        start_line = member.position.line
                        end_line = self.__calculate_end_line(start_line, member_string)

                        is_member_included = self.__is_implementation_included(
                            line_ranges, start_line, end_line
                        )

                        if is_member_included:
                            body.members.append(member_string)

                    model.body = str(body)

                result.append(model)

        return result
