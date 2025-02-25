from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Dict, Optional

import openai
from langchain_core.utils import from_env, secret_from_env
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_openai.chat_models.base import BaseChatOpenAI
from pydantic import ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

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
    DEFAULT_OPENROUTER_API_BASE,
    DEFAULT_OPENROUTER_LLM_MODEL,
    DEFAULT_OPENROUTER_MAX_TOKENS,
)
from autocommit_evaluation.core.enums import EnvironmentKey
from autocommit_evaluation.core.jira import Jira

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig


class ChatOpenRouter((BaseChatOpenAI)):
    model_name: str = Field(alias="model")
    """The name of the model"""
    api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None)
    )
    """OpenRouter API key"""
    api_base: str = Field(
        default_factory=from_env(
            "OPENROUTER_API_BASE", default=DEFAULT_OPENROUTER_API_BASE
        )
    )
    """OpenRouter API base URL"""

    model_config = ConfigDict(populate_by_name=True)

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return DEFAULT_OPENROUTER_LLM_MODEL

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids."""
        return {"api_key": "OPENROUTER_API_KEY"}

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        if self.api_base == DEFAULT_OPENROUTER_API_BASE and not (
            self.api_key and self.api_key.get_secret_value()
        ):
            raise ValueError(
                "If using default api base, OPENROUTER_API_KEY must be set."
            )
        client_params: dict = {
            k: v
            for k, v in {
                "api_key": self.api_key.get_secret_value() if self.api_key else None,
                "base_url": self.api_base,
                "timeout": self.request_timeout,
                "max_retries": self.max_retries,
                "default_headers": self.default_headers,
                "default_query": self.default_query,
            }.items()
            if v is not None
        }

        if not (self.client or None):
            sync_specific: dict = {"http_client": self.http_client}
            self.client = openai.OpenAI(
                **client_params, **sync_specific
            ).chat.completions
        if not (self.async_client or None):
            async_specific: dict = {"http_client": self.http_async_client}
            self.async_client = openai.AsyncOpenAI(
                **client_params, **async_specific
            ).chat.completions
        return self


jira = Jira()

# General Configs
__classification_llm_model = os.getenv(
    EnvironmentKey.CLASSIFICATION_LLM_MODEL.value, DEFAULT_OPENROUTER_LLM_MODEL
)

__diff_classifier_chat_model = ChatOpenRouter(
    model=__classification_llm_model,
    temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

__filter_chat_model = ChatOpenRouter(
    model=__classification_llm_model,
    temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    max_tokens=DEFAULT_OPENROUTER_MAX_TOKENS,
)

# OPEN AI Configs
__openai_llm_model = os.getenv(
    EnvironmentKey.OPENAI_LLM_MODEL.value, DEFAULT_OPENAI_LLM_MODEL
)
__openai_embedding_model = os.getenv(
    EnvironmentKey.OPENAI_EMBEDDING_MODEL.value, DEFAULT_OPENAI_EMBEDDINGS_MODEL
)

__openai_cmg_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_CMG_TEMPERATURE
)
__openai_query_text_chat_model = ChatOpenAI(
    model=__openai_llm_model, temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE
)

__openai_embeddings = OpenAIEmbeddings(model=__openai_embedding_model)

# OpenRouter Configs
__openrouter_llm_model = os.getenv(
    EnvironmentKey.OPENROUTER_LLM_MODEL.value, DEFAULT_OPENROUTER_LLM_MODEL
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

# Open AI Chains
openai_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __diff_classifier_chat_model
)
openai_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __diff_classifier_chat_model
)

openai_zero_shot_low_level_context_cmg_chain = (
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

openai_high_level_context_chain = HighLevelContextChain(
    __openai_query_text_chat_model, __filter_chat_model, __openai_embeddings
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
    __diff_classifier_chat_model
)
openrouter_high_level_context_diff_classifier_chain = (
    HighLevelContextDiffClassifierChain(__diff_classifier_chat_model)
)

openrouter_zero_shot_low_level_context_cmg_chain = (
    LowLevelContextCommitMessageGenerationChain(
        openrouter_low_level_context_diff_classifier_chain,
        __openrouter_cmg_chat_model,
        ZERO_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

openrouter_few_shot_low_level_context_cmg_chain = (
    LowLevelContextCommitMessageGenerationChain(
        openrouter_low_level_context_diff_classifier_chain,
        __openrouter_cmg_chat_model,
        FEW_SHOT_LOW_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)

openrouter_high_level_context_chain = HighLevelContextChain(
    __openrouter_query_text_chat_model,
    __filter_chat_model,
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
