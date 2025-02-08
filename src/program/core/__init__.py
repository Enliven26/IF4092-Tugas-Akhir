import os

from langchain_ollama import ChatOllama
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
    DEFAULT_DEEPSEEK_LLM_MODEL,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    DEFAULT_OPEN_AI_EMBEDDINGS_MODEL,
    DEFAULT_OPEN_AI_LLM_MODEL,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from core.enums import EnvironmentKey
from core.git import Git, IGit
from core.jira import IJira, Jira

git: IGit = Git()
jira: IJira = Jira()

# OPEN AI Configs
__open_ai_llm_model = os.getenv(
    EnvironmentKey.OPENAI_LLM_MODEL.value, DEFAULT_OPEN_AI_LLM_MODEL
)
__open_ai_embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, DEFAULT_OPEN_AI_EMBEDDINGS_MODEL
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

# DeekSeek Configs
__deepseek_llm_model = os.getenv(
    EnvironmentKey.DEEPSEEK_LLM_MODEL.value, DEFAULT_DEEPSEEK_LLM_MODEL
)
__deepseek_diff_classifier_chat_model = ChatOllama(
    model=__deepseek_llm_model, temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE
)

__deepseek_cmg_chat_model = ChatOllama(
    model=__deepseek_llm_model, temperature=DEFAULT_CMG_TEMPERATURE
)
__deepseek_query_text_chat_model = ChatOllama(
    model=__deepseek_llm_model, temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE, 
)
__deepseek_filter_chat_model = ChatOllama(
    model=__deepseek_llm_model, temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE
)

# Open AI Chains
open_ai_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)
open_ai_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)

open_ai_low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    open_ai_low_level_context_diff_classifier_chain, __open_ai_cmg_chat_model
)

open_ai_high_level_context_chain = HighLevelContextChain(
    __open_ai_query_text_chat_model, __open_ai_filter_chat_model, __open_ai_embeddings
)

open_ai_zero_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    open_ai_high_level_context_diff_classifier_chain,
    open_ai_high_level_context_chain,
    __open_ai_cmg_chat_model,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)

open_ai_few_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    open_ai_high_level_context_diff_classifier_chain,
    open_ai_high_level_context_chain,
    __open_ai_cmg_chat_model,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)

# DeepSeek Chains
deepseek_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __deepseek_diff_classifier_chat_model
)
deepseek_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __deepseek_diff_classifier_chat_model
)

deepseek_low_level_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    deepseek_low_level_context_diff_classifier_chain, __deepseek_cmg_chat_model
)

deepseek_high_level_context_chain = HighLevelContextChain(
    __deepseek_query_text_chat_model, __deepseek_filter_chat_model, __open_ai_embeddings
)

deepseek_zero_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    deepseek_high_level_context_diff_classifier_chain,
    deepseek_high_level_context_chain,
    __deepseek_cmg_chat_model,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)

deepseek_few_shot_high_level_cmg_chain = HighLevelContextCommitMessageGenerationChain(
    deepseek_high_level_context_diff_classifier_chain,
    deepseek_high_level_context_chain,
    __deepseek_cmg_chat_model,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
