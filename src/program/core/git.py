import logging
import subprocess
from abc import ABC, abstractmethod


class IGit(ABC):
    @abstractmethod
    def get_diff(
        self, repo_path: str, commit_hash: str, included_file_paths: set[str]
    ) -> str:
        pass


class Git(IGit):
    def get_diff(
        self, repo_path: str, commit_hash: str, included_file_paths: set[str]
    ) -> str:

        command = ["git", "-C", repo_path, "diff", f"{commit_hash}~1", commit_hash]

        if included_file_paths:
            command.extend(included_file_paths)

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout

        except subprocess.CalledProcessError:
            logging.exception("Error while running git diff:")
            return ""
