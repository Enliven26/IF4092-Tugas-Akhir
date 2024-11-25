import logging
import os

from dotenv import load_dotenv

from core.enums import EnvironmentKey
from core.git import Git
from core.parser import CodeParser, DiffParser


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    git = Git()
    diff_parser = DiffParser()

    source_repo_path = os.getenv(EnvironmentKey.SOURCE_REPO_PATH.value)

    included_file_paths = [
        "app/src/main/java/com/example/bondoman/views/fragments/SettingsFragment.kt",
        "app/src/main/java/com/example/bondoman/services/services/ExpiryService.kt",
    ]

    commit_hash = "5b7bb837085ae8c9949024dcda4a19f21fba84bd"

    diff = git.get_diff(source_repo_path, commit_hash, included_file_paths)

    file_diffs = diff_parser.get_diff_lines(diff, included_file_paths)

    pass

    # content = ""
    # code_parser = CodeParser()

    # implementations = code_parser.get_methods(content, [range(6,9)])

    # for implementation in implementations:
    #     print(implementation)


if __name__ == "__main__":
    main()
