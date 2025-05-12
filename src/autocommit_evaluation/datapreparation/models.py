from autocommit.core.models import BaseModel

class ExampleGenerationResultModel(BaseModel):
    diff = ""
    source_code = ""
    high_level_context = ""
    commit_message = ""
