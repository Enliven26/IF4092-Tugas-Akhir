import json
import os
import subprocess
import tempfile

from autocommit.core.parsers.language.base import ICodeParser


class JavaCodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def __run_java_parser(self, java_source_code: str, line_ranges: list[range]) -> str:
        temp_file_path = ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(java_source_code.encode("utf-8"))

        jar_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "jars", "javaparser.jar"
            )
        )
        line_ranges_json = json.dumps([[r.start, r.stop] for r in line_ranges])

        command = [
            "java",
            "-jar",
            jar_path,
            temp_file_path,
            line_ranges_json,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Error executing Java program: {result.stderr}")

    def get_declarations(self, source_code: str, line_ranges: list[range]) -> str:
        return self.__run_java_parser(source_code, line_ranges)
