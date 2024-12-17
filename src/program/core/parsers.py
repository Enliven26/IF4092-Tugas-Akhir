from abc import ABC, abstractmethod
from enum import Enum
from textwrap import indent

from core.enums import DiffVersion
from core.models import FileDiffModel
from diff_parser import Diff, DiffBlock
from kopyt import Parser, node


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
    def get_methods(self, source_code: str, line_ranges: list[range]) -> list[str]:
        pass


class _ImplementationType(Enum):
    INTERFACE = 0
    CLASS = 1
    FUNCTIONAL_INTERFACE = 2
    FUNCTION = 3
    OBJECT = 4


class _ClassImplementationModel:
    def __init__(self):
        self.modifiers: list[str] = []
        self.name: str = ""
        self.generics: str = ""
        self.constructor: str = ""
        self.supertypes: list[str] = []
        self.constraints: str = ""
        self.body: str = ""
        self.type: _ImplementationType = _ImplementationType.CLASS

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

        if self.type == _ImplementationType.INTERFACE:
            declaration = "interface"
        elif self.type == _ImplementationType.CLASS:
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


class _ClassBodyModel:
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


class _ObjectImplementationModel:
    def __init__(self):
        self.modifiers: list[str] = []
        self.name: str = ""
        self.supertypes: list[str] = []
        self.body: str = ""

    def __str__(self):
        modifiers = ""
        name = self.name
        supertypes = ""
        body = self.body

        if self.modifiers:
            modifiers = f"{' '.join(self.modifiers)} "

        if self.supertypes:
            supertypes = f" : {', '.join(self.supertypes)}"

        return f"{modifiers}object {name}{supertypes}{body}"


class CodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

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

    def __set_class_implementation_data(
        self, model: _ClassImplementationModel, declaration: node.ClassDeclaration
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
            model.type = _ImplementationType.INTERFACE
        elif isinstance(declaration, node.FunctionalInterfaceDeclaration):
            declaration = _ImplementationType.FUNCTIONAL_INTERFACE
        else:
            declaration = _ImplementationType.CLASS

    def __set_object_implementation_data(
        self, model: _ObjectImplementationModel, declaration: node.ObjectDeclaration
    ):
        model.modifiers = map(str, declaration.modifiers)
        model.name = declaration.name
        model.supertypes = map(str, declaration.supertypes)

    def __get_class_body(
        self, original_body: node.ClassBody, line_ranges: list[range]
    ) -> str:
        new_body = _ClassBodyModel()
        for member in original_body.members:
            start_line = member.start_position.line
            end_line = member.end_position.line

            is_member_included = self.__is_implementation_included(
                line_ranges, start_line, end_line
            )

            if is_member_included:
                new_body.members.append(str(member))

        return str(new_body)

    def get_methods(self, source_code: str, line_ranges: list[range]) -> list[str]:
        parser = Parser(source_code)
        parser_result = parser.parse()

        result: list[str] = []

        for declaration in parser_result.declarations:
            parent_start_line = declaration.start_position.line
            parent_end_line = declaration.end_position.line

            is_parent_included = self.__is_implementation_included(
                line_ranges, parent_start_line, parent_end_line
            )

            if not is_parent_included:
                continue

            if isinstance(declaration, node.ClassDeclaration):
                model = _ClassImplementationModel()
                self.__set_class_implementation_data(model, declaration)

                if isinstance(declaration.body, node.EnumClassBody):
                    model.body = str(declaration.body)

                else:
                    if declaration.body is not None:
                        model.body = self.__get_class_body(
                            declaration.body, line_ranges
                        )

                result.append(str(model))

            elif isinstance(declaration, node.ObjectDeclaration):
                model = _ObjectImplementationModel()

                self.__set_object_implementation_data(model, declaration)

                if declaration.body is not None:
                    model.body = self.__get_class_body(declaration.body, line_ranges)

                result.append(str(model))

            elif isinstance(declaration, node.FunctionDeclaration):
                result.append(str(declaration))

        return result
