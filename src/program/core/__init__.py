import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from core.chains import (
    HighLevelContextChain,
    HighLevelContextCommitMessageGenerationChain,
    HighLevelContextDiffClassifierChain,
    LowLevelContextCommitMessageGenerationChain,
    LowLevelContextDiffClassifierChain,
)
from core.constants import (
    DEFAULT_CMG_TEMPERATURE,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_EMBEDDINGS_MODEL,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.enums import EnvironmentKey
from core.git import Git, IGit
from core.jira import IJira, Jira

git: IGit = Git()
jira: IJira = Jira()

__open_ai_llm_model = os.getenv(
    EnvironmentKey.OPENAI_LLM_MODEL.value, DEFAULT_LLM_MODEL
)
__open_ai_embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, DEFAULT_EMBEDDINGS_MODEL
)

__open_ai_diff_classifier_chat_model = ChatOpenAI(
    model=__open_ai_llm_model, temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE
)

__open_ai_cmg_chat_model = ChatOpenAI(
    model=__open_ai_llm_model, temperature=DEFAULT_CMG_TEMPERATURE
)
__open_ai_query_text_chat_model = ChatOpenAI(
    model=__open_ai_llm_model, temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE
)
__open_ai_filter_chat_model = ChatOpenAI(
    model=__open_ai_llm_model, temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE
)
__open_ai_embeddings = OpenAIEmbeddings(model=__open_ai_embedding_model)

low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)
high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)

low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    low_level_context_diff_classifier_chain, __open_ai_cmg_chat_model
)

high_level_context_chain = HighLevelContextChain(
    __open_ai_query_text_chat_model, __open_ai_filter_chat_model, __open_ai_embeddings
)

zero_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    high_level_context_diff_classifier_chain,
    high_level_context_chain,
    __open_ai_cmg_chat_model,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)

few_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    high_level_context_diff_classifier_chain,
    high_level_context_chain,
    __open_ai_cmg_chat_model,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
