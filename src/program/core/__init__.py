import os

from core.chains import (
    HighLevelContextChain,
    HighLevelContextCommitMessageGenerationChain,
    HighLevelContextDiffClassifierChain,
    LowLevelContextCommitMessageGenerationChain,
    LowLevelContextDiffClassifierChain,
)
from core.constants import (
    DEFAULT_EMBEDDINGS_MODEL,
    DEFAULT_LLM_MODEL,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.enums import EnvironmentKey
from core.git import Git, IGit
from core.jira import IJira, Jira

git: IGit = Git()
jira: IJira = Jira()

__llm_model = os.getenv(EnvironmentKey.OPENAI_LLM_MODEL.value, DEFAULT_LLM_MODEL)
__embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, DEFAULT_EMBEDDINGS_MODEL
)

low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __llm_model, temperature=0
)
high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __llm_model, temperature=0
)

low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    low_level_context_diff_classifier_chain, __llm_model
)

high_level_context_chain = HighLevelContextChain(
    __llm_model, __embedding_model, __llm_model
)

zero_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    high_level_context_diff_classifier_chain,
    high_level_context_chain,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    __llm_model,
)

few_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    high_level_context_diff_classifier_chain,
    high_level_context_chain,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    __llm_model,
)
