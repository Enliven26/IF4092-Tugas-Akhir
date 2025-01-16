from abc import ABC

from core.models import CommitDataModel


class IProgramRunner(ABC):
    def _get_commits(self, path: str) -> list[CommitDataModel]:
        with open(path, "r", encoding="utf-8") as file:
            json_string = file.read()

        return CommitDataModel.from_json(json_string)
