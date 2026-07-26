import json
from abc import ABC, abstractmethod
from typing import Any

import httpx
from openai import APIError, APIStatusError, AsyncOpenAI

from resumesh_llm.core.exceptions import (
    ConfigurationError,
    ProviderError,
    RateLimitError,
)
from resumesh_llm.core.models import GenerationUsage, LLMRequest, LLMResponse


class LLMClient(ABC):
    """Abstract Base Class defining the standard LLM Client interface."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously generates a response from the LLM based on the request.

        Args:
            request: LLMRequest containing the prompt and parameters.

        Returns:
            LLMResponse containing the text output, usage stats, and metadata.

        Raises:
            ProviderError: If the provider returns an API error.
            RateLimitError: If rate limits are reached.
            LLMError: General LLM package exceptions.
        """
        pass


class MockClient(LLMClient):
    """Mock LLM client useful for development, CI/CD, and fast local prototyping."""

    def __init__(
        self, model_name: str = "mock-model", mock_response: str | None = None
    ):
        super().__init__(model_name)
        self.mock_response = mock_response

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Determine the response text.
        # If response_format is json_object, attempt to return a valid JSON structure.
        if self.mock_response is not None:
            text_response = self.mock_response
        else:
            if request.response_format == "json_object":
                text_response = json.dumps(
                    {
                        "summary": f"This is a mocked JSON summary response generated for prompt: {request.prompt[:30]}...",
                        "tags": ["mock", "test", "resumesh"],
                        "languages": ["Python", "TypeScript"],
                        "highlights": [
                            "Implemented mock provider client",
                            "Configured robust tests",
                        ],
                        "improvements": [
                            "Enhanced unit testing metrics",
                            "Refactored codebase to SOLID principles",
                        ],
                        "skills": ["Python", "FastAPI", "Docker"],
                        "score": 85,
                        "original": "Wrote some unit tests",
                        "optimized": "Designed and executed a robust test suite, achieving 95% branch coverage.",
                        "explanation": "Added actionable metrics and impact to emphasize software quality.",
                        "hard_skills": ["Python", "FastAPI", "PostgreSQL"],
                        "soft_skills": ["Leadership", "Agile Execution"],
                        "tools_and_platforms": ["Docker", "AWS", "Git"],
                        "match_score": 85,
                        "matching_skills": ["Python", "FastAPI"],
                        "missing_skills": ["Kubernetes", "GraphQL"],
                        "suggestions": [
                            "Add more direct impact metrics to your experience bullets."
                        ],
                    }
                )
            else:
                text_response = f"Mocked response for prompt: {request.prompt[:100]}"

        return LLMResponse(
            text=text_response,
            usage=GenerationUsage(
                prompt_tokens=10, completion_tokens=15, total_tokens=25
            ),
            provider="mock",
            model=self.model_name,
            raw_response={"status": "success", "mocked": True},
        )


class OpenAIClient(LLMClient):
    """Client for OpenAI services (GPT models)."""

    def __init__(
        self, api_key: str, model_name: str = "gpt-4o", base_url: str | None = None
    ):
        super().__init__(model_name)
        if not api_key:
            raise ConfigurationError("OpenAI API key must be provided.")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

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
            response = await self.client.chat.completions.create(**kwargs)
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
                provider="openai",
                model=self.model_name,
                raw_response=response.model_dump(),
            )

        except APIStatusError as e:
            if e.status_code == 429:
                raise RateLimitError(str(e), provider="openai") from e
            raise ProviderError(
                str(e), provider="openai", status_code=e.status_code
            ) from e
        except APIError as e:
            raise ProviderError(str(e), provider="openai") from e


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
            response = await self.client.chat.completions.create(**kwargs)
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


class OllamaClient(LLMClient):
    """Client for local Ollama API server."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model_name: str = "llama3"
    ):
        super().__init__(model_name)
        self.base_url = base_url.rstrip("/")
        # We configure a timeout default of 60 seconds since local execution might take longer
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "options": {
                "temperature": request.temperature,
            },
            "stream": False,
        }

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        if request.response_format == "json_object":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=self.timeout) as http_client:
            try:
                response = await http_client.post(
                    f"{self.base_url}/api/chat", json=payload
                )

                if response.status_code != 200:
                    raise ProviderError(
                        f"Ollama server returned error: {response.text}",
                        provider="ollama",
                        status_code=response.status_code,
                    )

                response_data = response.json()
                text = response_data.get("message", {}).get("content", "")

                # Extract Ollama usage data if available
                prompt_tokens = response_data.get("prompt_eval_count")
                completion_tokens = response_data.get("eval_count")

                usage_data = None
                if prompt_tokens is not None or completion_tokens is not None:
                    usage_data = GenerationUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=(prompt_tokens or 0) + (completion_tokens or 0),
                    )

                return LLMResponse(
                    text=text,
                    usage=usage_data,
                    provider="ollama",
                    model=self.model_name,
                    raw_response=response_data,
                )

            except httpx.RequestError as e:
                raise ProviderError(
                    f"HTTP request to Ollama failed: {str(e)}", provider="ollama"
                ) from e
