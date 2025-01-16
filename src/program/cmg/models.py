class CommitMessageGenerationResultModel:
    def __init__(self):
        self.generator_id: str = ""
        self.commit_message: str = ""


class EvaluationResultModel:
    def __init__(self):
        self.evaluation_id: str = ""
        self.generation_results: list[CommitMessageGenerationResultModel] = []
