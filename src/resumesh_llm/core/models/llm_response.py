from typing import Any

from pydantic import BaseModel, Field

from resumesh_llm.core.models.generation_usage import GenerationUsage


class LLMResponse(BaseModel):
    """Standardized response from the LLM client."""

    text: str = Field(description="The primary generated text content")
    usage: GenerationUsage | None = Field(
        default=None, description="Token usage details if provided by the model api"
    )
    provider: str = Field(description="The identifier of the LLM provider used")
    model: str = Field(description="The model name that generated the response")
    raw_response: dict[str, Any] | None = Field(
        default=None,
        description="Raw dictionary response from the provider for advanced tracking",
    )
