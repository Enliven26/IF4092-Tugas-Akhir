import os

from core.chains import (
    DataGenerationChain,
    DiffClassifierChain,
    DiffContextDocumentRetriever,
    HighLevelContextCommitMessageGenerationChain,
    LowLevelContextCommitMessageGenerationChain,
)
from core.constants import (
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.enums import EnvironmentKey
from core.git import Git
from core.parsers.language import JavaCodeParser

git = Git()



__DEFAULT_RETRIEVER_LOCAL_PATH = os.path.join("data", "context", "defaultretriever")
__RETRIEVER_DOCUMENT_PATH = os.path.join("data", "context", "highlevelcontext.txt")

__llm_model = os.getenv(EnvironmentKey.OPENAI_LLM_MODEL.value, "gpt-4o-mini")
__embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, "text-embedding-3-small"
)
default_document_retriever: DiffContextDocumentRetriever = None

if not os.path.exists(__DEFAULT_RETRIEVER_LOCAL_PATH) or not os.listdir(
    __DEFAULT_RETRIEVER_LOCAL_PATH
):
    os.makedirs(__DEFAULT_RETRIEVER_LOCAL_PATH, exist_ok=True)
    default_document_retriever = DiffContextDocumentRetriever.from_document_file(
        __RETRIEVER_DOCUMENT_PATH, __embedding_model, __llm_model
    )
    default_document_retriever.save(__DEFAULT_RETRIEVER_LOCAL_PATH)

else:
    default_document_retriever = DiffContextDocumentRetriever.from_local(
        __DEFAULT_RETRIEVER_LOCAL_PATH, __embedding_model, __llm_model
    )

diff_classifier_chain = DiffClassifierChain(__llm_model, temperature=0)

low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    diff_classifier_chain, __llm_model, temperature=0.7
)

zero_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    diff_classifier_chain,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    __llm_model,
    __llm_model,
    default_document_retriever,
    cmg_temperature=0.7,
    document_query_text_temperature=0.7,
)

few_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    diff_classifier_chain,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    __llm_model,
    __llm_model,
    default_document_retriever,
    cmg_temperature=0.7,
    document_query_text_temperature=0.7,
)

data_generation_chain = DataGenerationChain(__llm_model, temperature=0.7)
