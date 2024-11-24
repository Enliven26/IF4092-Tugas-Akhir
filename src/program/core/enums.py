from enum import Enum

class EnvironmentKey(Enum):
    SOURCE_PATH = "SOURCE_PATH"

class ImplementationType(Enum):
    INTERFACE = 0
    CLASS = 1
    FUNCTIONAL_INTERFACE = 2