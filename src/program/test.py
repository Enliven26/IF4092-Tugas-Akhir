import logging
import os

from dotenv import load_dotenv

from core.enums import DiffVersion, EnvironmentKey
from core.git import Git
from core.parser import CodeParser, DiffParser, ImplementationModel


def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()

    git = Git()
    diff_parser = DiffParser()
    code_parser = CodeParser()

    source_repo_path = os.getenv(EnvironmentKey.SOURCE_REPO_PATH.value)

    included_file_paths = [
        "app/src/main/java/com/example/bondoman/views/fragments/SettingsFragment.kt",
        "app/src/main/java/com/example/bondoman/services/services/ExpiryService.kt",
    ]

    current_commit_hash = "5b7bb837085ae8c9949024dcda4a19f21fba84bd"
    previous_commit_hash = f"{current_commit_hash}~1"
    diff = git.get_diff(
        source_repo_path, previous_commit_hash, current_commit_hash, included_file_paths
    )

    commit_map = {
        DiffVersion.OLD: previous_commit_hash,
        DiffVersion.NEW: current_commit_hash,
    }

    file_diffs = diff_parser.get_diff_lines(diff, included_file_paths)

    implementations: list[ImplementationModel] = []

    for file_diff in file_diffs:
        file_content = git.get_file_content(
            source_repo_path, commit_map[file_diff.version], file_diff.file_path
        )

        new_implementations = code_parser.get_methods(
            file_content, file_diff.line_ranges
        )
        implementations.extend(new_implementations)

    for implementation in implementations:
        print(implementation)


if __name__ == "__main__":
    main()
