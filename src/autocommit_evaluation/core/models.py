from __future__ import annotations

from typing import Dict, Optional

import openai
from langchain_core.utils import from_env, secret_from_env
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from pydantic import ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

from autocommit_evaluation.core.constants import (
    DEFAULT_OPENROUTER_API_BASE,
    DEFAULT_OPENROUTER_LLM_MODEL,
)


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


class ChatModelFactory:
    @staticmethod
    def create_chat_model(
        model: str, temperature: float = 1.0, **kwargs
    ) -> BaseChatOpenAI:
        splits = model.split("/")

        if len(splits) != 2:
            raise ValueError(f"Invalid model format: {model}")

        if splits[0] == "openai":
            return ChatOpenAI(model=splits[1], temperature=temperature, **kwargs)
        else:
            return ChatOpenRouter(model=model, temperature=temperature, **kwargs)
