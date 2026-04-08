from __future__ import annotations

import json
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings

T = TypeVar("T", bound=BaseModel)

_client: AsyncOpenAI | None = None


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
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = get_openai_client()

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
