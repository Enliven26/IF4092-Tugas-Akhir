import logging
import subprocess
from abc import ABC, abstractmethod


class IGit(ABC):
    @abstractmethod
    def get_diff(
        self,
        repo_path: str,
        previous_commit_hash: str,
        current_commit_hash: str,
        included_file_paths: list[str],
    ) -> str:
        pass

    @abstractmethod
    def get_file_content(self, repo_path: str, commit_hash: str, file_path: str) -> str:
        pass


class Git(IGit):
    def get_diff(
        self,
        repo_path: str,
        previous_commit_hash: str,
        current_commit_hash: str,
        included_file_paths: set[str],
    ) -> str:

        command = [
            "git",
            "-C",
            repo_path,
            "diff",
            previous_commit_hash,
            current_commit_hash,
        ]

        if included_file_paths:
            command.extend(included_file_paths)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError:
            logging.exception("Error while running git diff:")
            return ""

    def get_file_content(self, repo_path: str, commit_hash: str, file_path: str) -> str:
        command = ["git", "-C", repo_path, "show", f"{commit_hash}:{file_path}"]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError:
            logging.exception("Error while retrieving file content:")
            return ""
