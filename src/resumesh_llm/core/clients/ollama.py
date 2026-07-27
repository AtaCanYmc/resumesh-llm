from typing import Any

import httpx

from resumesh_llm.core.clients.base import LLMClient
from resumesh_llm.core.clients.retry import retry_with_backoff
from resumesh_llm.core.exceptions import ProviderError
from resumesh_llm.core.models.generation_usage import GenerationUsage
from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.models.llm_response import LLMResponse


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

                async def _call():
                    res = await http_client.post(
                        f"{self.base_url}/api/chat", json=payload
                    )
                    res.raise_for_status()
                    return res

                response = await retry_with_backoff(_call)

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

    async def generate_structured_output(
        self, request: LLMRequest, response_model: type
    ) -> Any:
        from resumesh_llm.core.clients.parser import OutputParser

        async def _call_and_parse():
            request.response_format = "json_object"
            res = await self.generate(request)
            return OutputParser.parse_and_validate(res.text, response_model)

        return await retry_with_backoff(_call_and_parse)
