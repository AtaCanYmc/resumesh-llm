from abc import ABC, abstractmethod
from typing import Any

from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.models.llm_response import LLMResponse


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

    @abstractmethod
    async def generate_structured_output(
        self, request: LLMRequest, response_model: type
    ) -> Any:
        """Asynchronously generates a structured response from the LLM based on a schema.

        Args:
            request: LLMRequest containing the prompt and parameters.
            response_model: Pydantic model class to parse the response into.

        Returns:
            An instance of response_model containing parsed fields.
        """
        pass

    async def generate_batch(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        """Asynchronously generates responses for multiple requests concurrently.

        Args:
            requests: List of LLMRequest objects.

        Returns:
            List of LLMResponse objects in the same order.
        """
        import asyncio

        return list(await asyncio.gather(*(self.generate(req) for req in requests)))

    async def generate_structured_output_batch(
        self, requests: list[tuple[LLMRequest, type]]
    ) -> list[Any]:
        """Asynchronously generates structured outputs for multiple requests concurrently.

        Args:
            requests: List of tuples containing (LLMRequest, Pydantic model class).

        Returns:
            List of parsed model instances.
        """
        import asyncio

        return list(
            await asyncio.gather(
                *(
                    self.generate_structured_output(req, model)
                    for req, model in requests
                )
            )
        )
