from enum import Enum


class EnvironmentKey(Enum):
    OPENAI_API_KEY = "OPENAI_API_KEY"
    OPENAI_LLM_MODEL = "OPENAI_LLM_MODEL"
    DATA_GENERATION_OUTPUT_PATH = "DATA_GENERATION_OUTPUT_PATH"
    CMG_OUTPUT_PATH = "CMG_OUTPUT_PATH"
    HIGH_LEVEL_CONTEXT_OUTPUT_PATH = "HIGH_LEVEL_CONTEXT_OUTPUT_PATH"
    DIFF_CLASSIFICATION_OUTPUT_PATH = "DIFF_CLASSIFICATION_OUTPUT_PATH"
    OPENAI_EMBEDDING_MODEL = "OPENAI_EMBEDDING_MODEL"


class DiffVersion(Enum):
    OLD = 0
    NEW = 1

    def __str__(self):
        if self == DiffVersion.OLD:
            return "Before"

        return "After"
