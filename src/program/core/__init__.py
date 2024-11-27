from core.chains import ICommitMessageGenerationChain, IDataGenerationChain
from core.git import Git
from core.models import CommitMessageGenerationPromptInputModel
from core.parsers import CodeParser, DiffParser

git = Git()
diff_parser = DiffParser()
code_parser = CodeParser()


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
