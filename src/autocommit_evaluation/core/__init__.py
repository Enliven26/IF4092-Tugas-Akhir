from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from autocommit.core.chains import (
    HighLevelContextChain,
    HighLevelContextCommitMessageGenerationChain,
    HighLevelContextDiffClassifierChain,
    LowLevelContextCommitMessageGenerationChain,
    LowLevelContextDiffClassifierChain,
)
from autocommit.core.constants import (
    DEFAULT_CMG_TEMPERATURE,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    DEFAULT_OPEN_AI_EMBEDDINGS_MODEL,
    DEFAULT_OPEN_AI_LLM_MODEL,
    DEFAULT_OPENROUTER_LLM_MODEL,
    DEFAULT_OPENROUTER_MAX_TOKENS,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from autocommit_evaluation.core.enums import EnvironmentKey
from autocommit_evaluation.core.jira import Jira

jira = Jira()

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

# OpenRouter Configs
__openrouter_llm_model = os.getenv(
    EnvironmentKey.OPENROUTER_LLM_MODEL.value, DEFAULT_OPENROUTER_LLM_MODEL
)


class ChatOpenRouter(ChatOpenAI):
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model,
            **kwargs,
        )


__openrouter_diff_classifier_chat_model = ChatOpenRouter(
    model=__openrouter_llm_model,
    temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

__openrouter_cmg_chat_model = ChatOpenRouter(
    model=__openrouter_llm_model,
    temperature=DEFAULT_CMG_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)
__openrouter_query_text_chat_model = ChatOpenRouter(
    model=__openrouter_llm_model,
    temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)
__openrouter_filter_chat_model = ChatOpenRouter(
    model=__openrouter_llm_model,
    temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

# Open AI Chains
open_ai_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)
open_ai_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __open_ai_diff_classifier_chat_model
)

open_ai_low_level_context_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    open_ai_low_level_context_diff_classifier_chain, __open_ai_cmg_chat_model
)

open_ai_high_level_context_chain = HighLevelContextChain(
    __open_ai_query_text_chat_model, __open_ai_filter_chat_model, __open_ai_embeddings
)

open_ai_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        open_ai_high_level_context_diff_classifier_chain,
        open_ai_high_level_context_chain,
        __open_ai_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

open_ai_few_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        open_ai_high_level_context_diff_classifier_chain,
        open_ai_high_level_context_chain,
        __open_ai_cmg_chat_model,
        FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

# OpenRouter Chains
openrouter_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __openrouter_diff_classifier_chat_model
)
openrouter_high_level_context_diff_classifier_chain = (
    HighLevelContextDiffClassifierChain(__openrouter_diff_classifier_chat_model)
)

openrouter_high_level_context_chain = HighLevelContextChain(
    __openrouter_query_text_chat_model,
    __openrouter_filter_chat_model,
    __open_ai_embeddings,
)

openrouter_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openrouter_high_level_context_diff_classifier_chain,
        openrouter_high_level_context_chain,
        __openrouter_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)
