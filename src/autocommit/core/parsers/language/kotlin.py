from enum import Enum
from textwrap import indent

from autocommit.core.parsers.language.base import ICodeParser
from autocommit.kopyt import Parser, node


class _KotlinImplementationType(Enum):
    INTERFACE = 0
    CLASS = 1
    FUNCTIONAL_INTERFACE = 2
    FUNCTION = 3
    OBJECT = 4


class _KotlinClassImplementationModel:
    def __init__(self):
        self.modifiers: list[str] = []
        self.name: str = ""
        self.generics: str = ""
        self.constructor: str = ""
        self.supertypes: list[str] = []
        self.constraints: str = ""
        self.body: str = ""
        self.type: _KotlinImplementationType = _KotlinImplementationType.CLASS

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

        if self.type == _KotlinImplementationType.INTERFACE:
            declaration = "interface"
        elif self.type == _KotlinImplementationType.CLASS:
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


class _KotlinClassBodyModel:
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


class _KotlinObjectImplementationModel:
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


class KotlinCodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def __is_declaration_included(
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
        self, model: _KotlinClassImplementationModel, declaration: node.ClassDeclaration
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
            model.type = _KotlinImplementationType.INTERFACE
        elif isinstance(declaration, node.FunctionalInterfaceDeclaration):
            declaration = _KotlinImplementationType.FUNCTIONAL_INTERFACE
        else:
            declaration = _KotlinImplementationType.CLASS

    def __set_object_implementation_data(
        self,
        model: _KotlinObjectImplementationModel,
        declaration: node.ObjectDeclaration,
    ):
        model.modifiers = map(str, declaration.modifiers)
        model.name = declaration.name
        model.supertypes = map(str, declaration.supertypes)

    def __get_class_body(
        self, original_body: node.ClassBody, line_ranges: list[range]
    ) -> str:
        new_body = _KotlinClassBodyModel()
        for member in original_body.members:
            start_line = member.start_position.line
            end_line = member.end_position.line

            is_member_included = self.__is_declaration_included(
                line_ranges, start_line, end_line
            )

            if is_member_included:
                new_body.members.append(str(member))

        return str(new_body)

    def get_declarations(self, source_code: str, line_ranges: list[range]) -> str:
        parser = Parser(source_code)
        parser_result = parser.parse()

        results: list[str] = []

        for declaration in parser_result.declarations:
            parent_start_line = declaration.start_position.line
            parent_end_line = declaration.end_position.line

            is_parent_included = self.__is_declaration_included(
                line_ranges, parent_start_line, parent_end_line
            )

            if not is_parent_included:
                continue

            if isinstance(declaration, node.ClassDeclaration):
                model = _KotlinClassImplementationModel()
                self.__set_class_implementation_data(model, declaration)

                if isinstance(declaration.body, node.EnumClassBody):
                    model.body = str(declaration.body)

                else:
                    if declaration.body is not None:
                        model.body = self.__get_class_body(
                            declaration.body, line_ranges
                        )

                results.append(str(model))

            elif isinstance(declaration, node.ObjectDeclaration):
                model = _KotlinObjectImplementationModel()

                self.__set_object_implementation_data(model, declaration)

                if declaration.body is not None:
                    model.body = self.__get_class_body(declaration.body, line_ranges)

                results.append(str(model))

            elif isinstance(declaration, node.FunctionDeclaration):
                results.append(str(declaration))

        return "\n".join(results)
