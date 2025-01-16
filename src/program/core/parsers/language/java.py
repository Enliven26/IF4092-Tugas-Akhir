import subprocess
import json
from core.parsers.language.base import ICodeParser


class JavaCodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def __run_java_parser(java_source_code: str, line_ranges: list[range]) -> str:
        target_dir = "java\\javaparser\\target\\classes\\tugasakhir\\javaparser"
        line_ranges_json = json.dumps(line_ranges)

        classpath = f"{target_dir}/classes:{target_dir}/lib/*"

        command = [
            "java",
            "JavaParser",
            java_source_code,
            line_ranges_json
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Error executing Java program: {result.stderr}")


    def get_declarations(self, source_code: str, line_ranges: list[range]) -> list[str]:
        return self.__run_java_parser(source_code, line_ranges)
