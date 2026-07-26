from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class GenerationUsage(BaseModel):
    """Token usage details for the generated output."""
    prompt_tokens: Optional[int] = Field(default=None, description="Number of tokens in the input prompt")
    completion_tokens: Optional[int] = Field(default=None, description="Number of tokens in the generated response")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens used (prompt + completion)")


class LLMResponse(BaseModel):
    """Standardized response from the LLM client."""
    text: str = Field(description="The primary generated text content")
    usage: Optional[GenerationUsage] = Field(default=None, description="Token usage details if provided by the model api")
    provider: str = Field(description="The identifier of the LLM provider used")
    model: str = Field(description="The model name that generated the response")
    raw_response: Optional[Dict[str, Any]] = Field(default=None, description="Raw dictionary response from the provider for advanced tracking")


class LLMRequest(BaseModel):
    """Parameters for invoking an LLM."""
    prompt: str = Field(description="The main prompt for the LLM")
    system_instruction: Optional[str] = Field(default=None, description="System-level instructions / developer prompt to set LLM behavior")
    temperature: float = Field(default=0.7, description="Controls randomness. Lower is more deterministic")
    max_tokens: Optional[int] = Field(default=None, description="Maximum number of tokens to generate")
    response_format: Optional[str] = Field(default=None, description="Either 'text' or 'json_object'")
