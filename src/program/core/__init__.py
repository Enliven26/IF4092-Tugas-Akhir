from core.chains import ICommitMessageGenerationChain, IDataGenerationChain, DataGenerationChain
from core.git import Git
from core.models import CommitMessageGenerationPromptInputModel
from core.parsers import CodeParser, DiffParser
import os
from core.enums import EnvironmentKey

git = Git()
diff_parser = DiffParser()
code_parser = CodeParser()

__model = os.getenv(EnvironmentKey.OPENAI_MODEL.value, "gpt-4o-mini")
data_generation_chain = DataGenerationChain(__model)


class MockCommitMessageGenerationChain(ICommitMessageGenerationChain):
    def generate_commit_message(
        self, prompt_input: CommitMessageGenerationPromptInputModel
    ) -> str:
        return "Mock commit message"


mock_commit_message_generation_chain = MockCommitMessageGenerationChain()


class MockDataGenerationChain(IDataGenerationChain):
    def generate_high_level_context(self, diff: str) -> str:
        return "Mock high level context"


mock_data_generation_chain = MockDataGenerationChain()
