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
