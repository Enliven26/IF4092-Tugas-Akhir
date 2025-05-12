from autocommit.core.models import BaseModel

class CommitMessageGenerationResultModel(BaseModel):
    generator_id: str = ""
    commit_message: str = ""


class EvaluationResultModel(BaseModel):
    evaluation_id: str = ""
    commit_url: str = ""
    jira_url: str = ""
    included_file_paths: list[str] = []
    generation_results: list[CommitMessageGenerationResultModel] = []
