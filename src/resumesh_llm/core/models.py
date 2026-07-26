from typing import Any

from pydantic import BaseModel, Field


class GenerationUsage(BaseModel):
    """Token usage details for the generated output."""

    prompt_tokens: int | None = Field(
        default=None, description="Number of tokens in the input prompt"
    )
    completion_tokens: int | None = Field(
        default=None, description="Number of tokens in the generated response"
    )
    total_tokens: int | None = Field(
        default=None, description="Total tokens used (prompt + completion)"
    )


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


class LLMRequest(BaseModel):
    """Parameters for invoking an LLM."""

    prompt: str = Field(description="The main prompt for the LLM")
    system_instruction: str | None = Field(
        default=None,
        description="System-level instructions / developer prompt to set LLM behavior",
    )
    temperature: float = Field(
        default=0.7, description="Controls randomness. Lower is more deterministic"
    )
    max_tokens: int | None = Field(
        default=None, description="Maximum number of tokens to generate"
    )
    response_format: str | None = Field(
        default=None, description="Either 'text' or 'json_object'"
    )
