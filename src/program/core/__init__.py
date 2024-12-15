import os

from core.chains import (
    BaseCommitMessageGenerationChain,
    BaseDataGenerationChain,
    DataGenerationChain,
    HighLevelContextCommitMessageGenerationChain,
    HighLevelContextDocumentRetriever,
    LowLevelContextCommitMessageGenerationChain,
)
from core.enums import EnvironmentKey
from core.git import Git
from core.models import CommitMessageGenerationPromptInputModel
from core.parsers import CodeParser, DiffParser

git = Git()
diff_parser = DiffParser()
code_parser = CodeParser()


__DEFAULT_RETRIEVER_LOCAL_PATH = os.path.join("data", "context", "defaultretriever")
__RETRIEVER_DOCUMENT_PATH = os.path.join("data", "context", "highlevelcontext.txt")

default_document_retriever: HighLevelContextDocumentRetriever = None

if not os.path.exists(__DEFAULT_RETRIEVER_LOCAL_PATH) or not os.listdir(
    __DEFAULT_RETRIEVER_LOCAL_PATH
):
    os.makedirs(__DEFAULT_RETRIEVER_LOCAL_PATH, exist_ok=True)
    default_document_retriever = HighLevelContextDocumentRetriever.from_document_file(
        __RETRIEVER_DOCUMENT_PATH
    )
    default_document_retriever.save(__DEFAULT_RETRIEVER_LOCAL_PATH)

else:
    default_document_retriever = HighLevelContextDocumentRetriever.from_local(
        __DEFAULT_RETRIEVER_LOCAL_PATH
    )


__model = os.getenv(EnvironmentKey.OPENAI_MODEL.value, "gpt-4o-mini")

low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    __model, temperature=0.7
)

high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    __model,
    __model,
    default_document_retriever,
    cmg_temperature=0.7,
    document_query_text_temperature=0.7,
)

data_generation_chain = DataGenerationChain(__model, temperature=0.7)


class MockCommitMessageGenerationChain(BaseCommitMessageGenerationChain):
    def invoke(self, prompt_input: CommitMessageGenerationPromptInputModel) -> str:
        return "Mock commit message"

    def batch(
        self, prompt_inputs: list[CommitMessageGenerationPromptInputModel]
    ) -> list[str]:
        return ["Mock commit message"] * len(prompt_inputs)


mock_commit_message_generation_chain = MockCommitMessageGenerationChain()


class MockDataGenerationChain(BaseDataGenerationChain):
    def invoke(self, diff: str) -> str:
        return "Mock high level context"

    def batch(self, diffs: list[str]) -> list[str]:
        return ["Mock high level context"] * len(diffs)


mock_data_generation_chain = MockDataGenerationChain()
