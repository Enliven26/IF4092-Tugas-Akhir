from __future__ import annotations

import os

from langchain_core.utils import from_env, secret_from_env
from langchain_openai import OpenAIEmbeddings

from autocommit.core.chains import (
    HighLevelContextChain,
    HighLevelContextCommitMessageGenerationChain,
    HighLevelContextDiffClassifierChain,
    LowLevelContextCommitMessageGenerationChain,
    LowLevelContextDiffClassifierChain,
)
from autocommit.core.constants import (
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from autocommit_evaluation.core.constants import (
    DEFAULT_CMG_TEMPERATURE,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    DEFAULT_OPENAI_EMBEDDINGS_MODEL,
    DEFAULT_OPENAI_LLM_MODEL,
    DEFAULT_OPENROUTER_LLM_MODEL,
    DEFAULT_OPENROUTER_MAX_TOKENS,
)
from autocommit_evaluation.core.enums import EnvironmentKey
from autocommit_evaluation.core.jira import Jira
from autocommit_evaluation.core.models import ChatModelFactory

jira = Jira()

# General Configs
__classification_llm_model = os.getenv(
    EnvironmentKey.CLASSIFICATION_LLM_MODEL.value, DEFAULT_OPENROUTER_LLM_MODEL
)

__diff_classifier_chat_model = ChatModelFactory.create_chat_model(
    model=__classification_llm_model,
    temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

__filter_chat_model = ChatModelFactory.create_chat_model(
    model=__classification_llm_model,
    temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

# OPEN AI Configs
__openai_llm_model = os.getenv(
    EnvironmentKey.BASELINE_LLM_MODEL.value, DEFAULT_OPENAI_LLM_MODEL
)
__openai_embedding_model = os.getenv(
    EnvironmentKey.BASELINE_EMBEDDING_MODEL.value, DEFAULT_OPENAI_EMBEDDINGS_MODEL
)

__openai_cmg_chat_model = ChatModelFactory.create_chat_model(
    model=__openai_llm_model, temperature=DEFAULT_CMG_TEMPERATURE
)
__openai_query_text_chat_model = ChatModelFactory.create_chat_model(
    model=__openai_llm_model, temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE
)

__openai_embeddings = OpenAIEmbeddings(model=__openai_embedding_model)

# OpenRouter Configs
__openrouter_llm_model = os.getenv(
    EnvironmentKey.MAIN_LLM_MODEL.value, DEFAULT_OPENROUTER_LLM_MODEL
)

__openrouter_cmg_chat_model = ChatModelFactory.create_chat_model(
    model=__openrouter_llm_model,
    temperature=DEFAULT_CMG_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)
__openrouter_query_text_chat_model = ChatModelFactory.create_chat_model(
    model=__openrouter_llm_model,
    temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

# Open AI Chains
openai_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __diff_classifier_chat_model
)
openai_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __diff_classifier_chat_model
)

baseline_zero_shot_low_level_context_cmg_chain = (
    LowLevelContextCommitMessageGenerationChain(
        openai_low_level_context_diff_classifier_chain,
        __openai_cmg_chat_model,
        ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

openai_few_shot_low_level_context_cmg_chain = (
    LowLevelContextCommitMessageGenerationChain(
        openai_low_level_context_diff_classifier_chain,
        __openai_cmg_chat_model,
        FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

baseline_high_level_context_chain = HighLevelContextChain(
    __openai_query_text_chat_model, __filter_chat_model, __openai_embeddings
)

baseline_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openai_high_level_context_diff_classifier_chain,
        baseline_high_level_context_chain,
        __openai_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

baseline_few_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openai_high_level_context_diff_classifier_chain,
        baseline_high_level_context_chain,
        __openai_cmg_chat_model,
        FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

# OpenRouter Chains
openrouter_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __diff_classifier_chat_model
)
openrouter_high_level_context_diff_classifier_chain = (
    HighLevelContextDiffClassifierChain(__diff_classifier_chat_model)
)

main_zero_shot_low_level_context_cmg_chain = (
    LowLevelContextCommitMessageGenerationChain(
        openrouter_low_level_context_diff_classifier_chain,
        __openrouter_cmg_chat_model,
        ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

main_few_shot_low_level_context_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    openrouter_low_level_context_diff_classifier_chain,
    __openrouter_cmg_chat_model,
    FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)

main_high_level_context_chain = HighLevelContextChain(
    __openrouter_query_text_chat_model,
    __filter_chat_model,
    __openai_embeddings,
)

main_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openrouter_high_level_context_diff_classifier_chain,
        main_high_level_context_chain,
        __openrouter_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

main_few_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openrouter_high_level_context_diff_classifier_chain,
        main_high_level_context_chain,
        __openrouter_cmg_chat_model,
        FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)
