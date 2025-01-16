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
        is_zero_unified: bool = False,
    ) -> str:
        pass

    @abstractmethod
    def get_file_content(self, repo_path: str, commit_hash: str, file_path: str) -> str:
        pass

    @abstractmethod
    def get_commit_message(self, repo_path: str, commit_hash: str) -> str:
        pass


class Git(IGit):
    def get_diff(
        self,
        repo_path: str,
        previous_commit_hash: str,
        current_commit_hash: str,
        included_file_paths: set[str],
        is_zero_unified: bool = False,
    ) -> str:

        command = [
            "git",
            "-C",
            repo_path,
            "diff",
            "--unified=0" if is_zero_unified else "",
            previous_commit_hash,
            current_commit_hash,
        ]

        command = [arg for arg in command if arg]

        if included_file_paths:
            command.append("--")
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

    def get_commit_message(self, repo_path: str, commit_hash: str) -> str:
        command = ["git", "-C", repo_path, "log", "-1", "--pretty=%B", commit_hash]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError:
            logging.exception("Error while retrieving commit message:")
            return ""