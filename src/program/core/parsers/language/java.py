from javalang.tree import CompilationUnit
import javalang
import javalang.tree
from typing import Optional

from core.parsers.language.base import ICodeParser


class JavaCodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def __get_method_start_end(self, tree: CompilationUnit, method_node: CompilationUnit) -> tuple[
        Optional[int], Optional[int]]:

        startline = None
        endline = None
        for path, node in tree:
            if startline is not None and method_node not in path:
                endline = int(node.position.line) if node.position is not None else None
                break
            if startline is None and node == method_node:
                startline = int(node.position.line) if node.position is not None else None
                
        return startline, endline

    def __get_declaration_text(
            self, 
            code_lines: list[str], 
            start_line: int,
            end_line: int,
            last_endline_index: Optional[int] = None) -> tuple[str, int]:

        startline_index = start_line - 1 
        endline_index = end_line - 1

        # 1. check for and fetch annotations
        if last_endline_index is not None:
            for line in code_lines[(last_endline_index + 1):(startline_index)]:
                if "@" in line: 
                    startline_index = startline_index - 1
        declaration_text = "<ST>".join(code_lines[startline_index:endline_index])
        declaration_text = declaration_text[:declaration_text.rfind("}") + 1] 

        # 2. remove trailing rbrace for last methods & any external content/comments
        if not abs(declaration_text.count("}") - declaration_text.count("{")) == 0:
            # imbalanced braces
            brace_diff = abs(declaration_text.count("}") - declaration_text.count("{"))

            for _ in range(brace_diff):
                declaration_text = declaration_text[:declaration_text.rfind("}")]    
                declaration_text = declaration_text[:declaration_text.rfind("}") + 1]     

        meth_lines = declaration_text.split("<ST>")  
        declaration_text = "".join(meth_lines)                   
        last_endline_index = startline_index + (len(meth_lines) - 1) 

        return declaration_text, (startline_index + 1), (last_endline_index + 1), last_endline_index
        
    def __get_class_declaration_text(
            self, 
            code_lines: list[str],
            line_ranges: list[range],
            class_node: javalang.tree.ClassDeclaration,
            last_endline_index: Optional[int] = None
            ) -> tuple[str, int]:
        
        declaration_text = ""
        
        for _, node in class_node:
            start_line, end_line = self.__get_method_start_end(class_node, node)
            if start_line is None:
                continue
            if end_line is None:
                end_line = len(code_lines) + 1

            if not self.__is_declaration_included(line_ranges, start_line, end_line):
                continue

            text, last_endline_index = self.__get_declaration_text(
                code_lines, start_line, end_line, last_endline_index
            )

            declaration_text += text

        return declaration_text, last_endline_index

    def __is_declaration_included(self, line_ranges: list[range], start_line: int, end_line: int) -> bool:
        for line_range in line_ranges:
            if not (start_line > line_range.stop or end_line - 1 < line_range.start):
                return True
            
        return False

    def get_declarations(self, source_code: str, line_ranges: list[range]) -> list[str]:
        tree = javalang.parse.parse(source_code)
        result: list[str] = []
        code_lines = source_code.split("\n")
        lex = None

        for _, node in tree:
            declaration_text = ""

            start_line, end_line = self.__get_method_start_end(tree, node)
            
            if start_line is None:
                continue

            if end_line is None:
                end_line = len(code_lines) + 1

            if not self.__is_declaration_included(line_ranges, start_line, end_line):
                continue

            if isinstance(node, javalang.tree.ClassDeclaration):
                declaration_text, lex = self.__get_class_declaration_text(source_code, tree, node)

            else:
                declaration_text, lex = self.__get_declaration_text(code_lines, start_line, end_line, lex)

            result.append(declaration_text)

        return result
