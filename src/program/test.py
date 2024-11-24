import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from core.parser import CodeParser


def main():
    load_dotenv()
    source_path = os.getenv(EnvironmentKey.SOURCE_PATH.value)

    test_file_path = os.path.join(
        source_path,
        "app",
        "src",
        "main",
        "java",
        "com",
        "example",
        "bondoman",
        "data",
        "viewmodels",
        "transaction",
        "TransactionViewModel.kt",
    )

    content = ""

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = "".join(file.readlines())

    code_parser = CodeParser()

    implementations = code_parser.get_methods(content, [range(21, 21), range(38, 39)])

    for implementation in implementations:
        print(implementation)


if __name__ == "__main__":
    main()
