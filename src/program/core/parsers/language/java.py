import json
import os
import subprocess

from core.parsers.language.base import ICodeParser


class JavaCodeParser(ICodeParser):
    def __init__(self):
        super().__init__()

    def __run_java_parser(self, java_source_code: str, line_ranges: list[range]) -> str:
        target_dir = "..\\java\\javaparser\\target"
        target_dir = os.path.join("..", "java", "javaparser", "target")

        line_ranges_json = json.dumps([[r.start, r.stop] for r in line_ranges])
        classes_dir = os.path.join(target_dir, "classes")
        lib_dir = os.path.join(target_dir, "lib", "*")
        classpath = os.pathsep.join([classes_dir, lib_dir])
        main_class = "tugasakhir.javaparser.JavaParser"

        command = [
            "java",
            "-cp",
            classpath,
            main_class,
            java_source_code,
            line_ranges_json,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Error executing Java program: {result.stderr}")

    def get_declarations(self, source_code: str, line_ranges: list[range]) -> str:
        return self.__run_java_parser(source_code, line_ranges)
