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
    DEFAULT_OPENAI_EMBEDDINGS_MODEL,
    DEFAULT_OPENAI_LLM_MODEL,
    DEFAULT_OPENROUTER_LLM_MODEL,
    DEFAULT_OPENROUTER_MAX_TOKENS,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from autocommit_evaluation.core.enums import EnvironmentKey
from autocommit_evaluation.core.jira import Jira

jira = Jira()

# OPEN AI Configs
__openai_llm_model = os.getenv(
    EnvironmentKey.OPENAI_LLM_MODEL.value, DEFAULT_OPENAI_LLM_MODEL
)
__openai_embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, DEFAULT_OPENAI_EMBEDDINGS_MODEL
)

__openai_diff_classifier_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE
)

__openai_cmg_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_CMG_TEMPERATURE
)
__openai_query_text_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE
)
__openai_filter_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE
)
__openai_embeddings = OpenAIEmbeddings(model=__openai_embedding_model)

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
openai_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __openai_diff_classifier_chat_model
)
openai_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __openai_diff_classifier_chat_model
)

openai_low_level_context_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    openai_low_level_context_diff_classifier_chain, __openai_cmg_chat_model
)

openai_high_level_context_chain = HighLevelContextChain(
    __openai_query_text_chat_model, __openai_filter_chat_model, __openai_embeddings
)

openai_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openai_high_level_context_diff_classifier_chain,
        openai_high_level_context_chain,
        __openai_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

openai_few_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openai_high_level_context_diff_classifier_chain,
        openai_high_level_context_chain,
        __openai_cmg_chat_model,
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

openrouter_low_level_context_cmg_chain = LowLevelContextCommitMessageGenerationChain(
    openrouter_low_level_context_diff_classifier_chain, __openrouter_cmg_chat_model
)

openrouter_high_level_context_chain = HighLevelContextChain(
    __openrouter_query_text_chat_model,
    __openrouter_filter_chat_model,
    __openai_embeddings,
)

openrouter_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openrouter_high_level_context_diff_classifier_chain,
        openrouter_high_level_context_chain,
        __openrouter_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

openrouter_few_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        openrouter_high_level_context_diff_classifier_chain,
        openrouter_high_level_context_chain,
        __openrouter_cmg_chat_model,
        FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)
