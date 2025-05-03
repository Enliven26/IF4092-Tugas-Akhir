from autocommit.core.models import BaseModel

class ExampleGenerationResultModel(BaseModel):
    def __init__(self):
        self.diff = ""
        self.source_code = ""
        self.high_level_context = ""
        self.commit_message = ""
