from enum import Enum


class EnvironmentKey(Enum):
    SOURCE_REPO_PATH = "SOURCE_REPO_PATH"
    DATA_GENERATION_OUTPUT_PATH = "DATA_GENERATION_OUTPUT_PATH"
    EVALUATION_OUTPUT_PATH = "EVALUATION_OUTPUT_PATH"


class ImplementationType(Enum):
    INTERFACE = 0
    CLASS = 1
    FUNCTIONAL_INTERFACE = 2


class DiffVersion(Enum):
    OLD = (0,)
    NEW = 1
