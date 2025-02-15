from enum import Enum


class DiffVersion(Enum):
    OLD = 0
    NEW = 1

    def __str__(self):
        if self == DiffVersion.OLD:
            return "Before"

        return "After"
