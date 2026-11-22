from __future__ import annotations

import json
from typing import Any, TypeVar

from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from app.core.config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)

_client: AsyncOpenAI | None = None

# Expected failure modes when calling an LLM: the SDK's own errors (network/API),
# the missing-key RuntimeError from get_openai_client, and the parse/validation
# errors from turning a response into a model. Services catch these to fall back to
# deterministic behavior; anything outside this set is a real bug and propagates.
LLM_ERRORS: tuple[type[Exception], ...] = (
    OpenAIError,
    RuntimeError,
    json.JSONDecodeError,
    ValidationError,
    ValueError,
    KeyError,
    TypeError,
    IndexError,
)


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        api_key = settings.effective_llm_api_key
        if not api_key:
            raise RuntimeError("No LLM API key configured.")
        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if settings.effective_llm_base_url:
            client_kwargs["base_url"] = settings.effective_llm_base_url
        _client = AsyncOpenAI(**client_kwargs)
    return _client


async def close_openai_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


class OpenAIStructuredService:
    def __init__(self, client: AsyncOpenAI | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        # The client is resolved lazily so this service (and the classifier/enrichment
        # services that build it) can be constructed without an API key configured.
        # The key is only required when a completion is actually requested.
        self._client = client

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = get_openai_client()
        return self._client

    async def complete_json(self, *, prompt: str, response_model: type[T]) -> T:
        response = await self.client.responses.create(
            model=self.settings.llm_model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Return only valid JSON matching the requested schema.",
                        }
                    ],
                },
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
        )
        text = response.output_text
        data = json.loads(text)
        return response_model.model_validate(data)

    async def complete_list(self, *, prompt: str) -> list[str]:
        response = await self.client.responses.create(
            model=self.settings.llm_model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Return only a JSON object with a `companies` array of strings.",
                        }
                    ],
                },
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
        )
        payload: dict[str, Any] = json.loads(response.output_text)
        companies = payload.get("companies", [])
        return [company.strip() for company in companies if isinstance(company, str) and company.strip()]
