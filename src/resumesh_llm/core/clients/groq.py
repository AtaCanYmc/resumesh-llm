from typing import Any

from openai import APIError, APIStatusError, AsyncOpenAI

from resumesh_llm.core.clients.base import LLMClient
from resumesh_llm.core.clients.retry import retry_with_backoff
from resumesh_llm.core.exceptions import (
    ConfigurationError,
    ProviderError,
    RateLimitError,
)
from resumesh_llm.core.models.generation_usage import GenerationUsage
from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.models.llm_response import LLMResponse


class GroqClient(LLMClient):
    """Client for Groq cloud API utilizing the OpenAI compatible endpoint."""

    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        super().__init__(model_name)
        if not api_key:
            raise ConfigurationError("Groq API key must be provided.")
        # Groq uses the same OpenAI specification
        self.client = AsyncOpenAI(
            api_key=api_key, base_url="https://api.groq.com/openai/v1"
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": request.temperature,
        }

        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens

        if request.response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}

        try:

            async def _call():
                return await self.client.chat.completions.create(**kwargs)

            response = await retry_with_backoff(_call)
            choice = response.choices[0]
            text = choice.message.content or ""

            usage_data = None
            if response.usage:
                usage_data = GenerationUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

            return LLMResponse(
                text=text,
                usage=usage_data,
                provider="groq",
                model=self.model_name,
                raw_response=response.model_dump(),
            )

        except APIStatusError as e:
            if e.status_code == 429:
                raise RateLimitError(str(e), provider="groq") from e
            raise ProviderError(
                str(e), provider="groq", status_code=e.status_code
            ) from e
        except APIError as e:
            raise ProviderError(str(e), provider="groq") from e

    async def generate_structured_output(
        self, request: LLMRequest, response_model: type
    ) -> Any:
        request.response_format = "json_object"
        res = await self.generate(request)
        return response_model.model_validate_json(res.text)
