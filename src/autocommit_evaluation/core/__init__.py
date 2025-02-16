from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any, Optional

from langchain_core.language_models.base import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
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
    DEFAULT_DEEPSEEK_LLM_MODEL,
    DEFAULT_DEEPSEEK_MAX_TOKENS,
    DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    DEFAULT_OPEN_AI_EMBEDDINGS_MODEL,
    DEFAULT_OPEN_AI_LLM_MODEL,
    FEW_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
)
from autocommit_evaluation.core.enums import EnvironmentKey
from autocommit_evaluation.core.jira import Jira

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig

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

# DeekSeek Configs
__deepseek_llm_model = os.getenv(
    EnvironmentKey.DEEPSEEK_LLM_MODEL.value, DEFAULT_DEEPSEEK_LLM_MODEL
)


class _FilteredChatOllama(ChatOllama):
    def __filter_think_section(self, text: str) -> str:
        """Removes the <think>...</think> section from the response text."""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    def invoke(
        self,
        input: LanguageModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> BaseMessage:
        """Override invoke() to filter out <think>...</think> from the response."""
        response = super().invoke(input, config, stop=stop, **kwargs)

        # Filter out <think>...</think> section
        response.content = self.__filter_think_section(response.content)

        return response

    async def ainvoke(
        self,
        input: LanguageModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> BaseMessage:
        """Override ainvoke() (async version) to filter out <think>...</think> from the response."""
        response = await super().ainvoke(input, config, stop=stop, **kwargs)

        # Filter out <think>...</think> section
        response.content = self.__filter_think_section(response.content)

        return response


__deepseek_diff_classifier_chat_model = ChatDeepSeek(
    model=__deepseek_llm_model,
    temperature=DEFAULT_DIFF_CLASSIFIER_TEMPERATURE,
    max_tokens=DEFAULT_DEEPSEEK_MAX_TOKENS,
)

__deepseek_cmg_chat_model = ChatDeepSeek(
    model=__deepseek_llm_model,
    temperature=DEFAULT_CMG_TEMPERATURE,
    max_tokens=DEFAULT_DEEPSEEK_MAX_TOKENS,
)
__deepseek_query_text_chat_model = ChatDeepSeek(
    model=__deepseek_llm_model,
    temperature=DEFAULT_LLM_QUERY_TEXT_TEMPERATURE,
    max_tokens=DEFAULT_DEEPSEEK_MAX_TOKENS,
)
__deepseek_filter_chat_model = ChatDeepSeek(
    model=__deepseek_llm_model,
    temperature=DEFAULT_LLM_RETRIEVAL_FILTER_TEMPERATURE,
    max_tokens=DEFAULT_DEEPSEEK_MAX_TOKENS,
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

# DeepSeek Chains
deepseek_low_level_context_diff_classifier_chain = LowLevelContextDiffClassifierChain(
    __deepseek_diff_classifier_chat_model
)
deepseek_high_level_context_diff_classifier_chain = HighLevelContextDiffClassifierChain(
    __deepseek_diff_classifier_chat_model
)

deepseek_high_level_context_chain = HighLevelContextChain(
    __deepseek_query_text_chat_model, __deepseek_filter_chat_model, __open_ai_embeddings
)

deepseek_zero_shot_high_level_context_cmg_chain = (
    HighLevelContextCommitMessageGenerationChain(
        deepseek_high_level_context_diff_classifier_chain,
        deepseek_high_level_context_chain,
        __deepseek_cmg_chat_model,
        ZERO_SHOT_HIGH_LEVEL_CONTEXT_CMG_PROMPT_TEMPLATE,
    )
)
