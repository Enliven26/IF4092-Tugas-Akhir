class CommitMessageGenerationResultModel:
    def __init__(self):
        self.generator_id: str = ""
        self.commit_message: str = ""


class EvaluationResultModel:
    def __init__(self):
        self.evaluation_id: str = ""
        self.commit_url: str = ""
        self.jira_url: str = ""
        self.included_file_paths: list[str] = []
        self.generation_results: list[CommitMessageGenerationResultModel] = []
