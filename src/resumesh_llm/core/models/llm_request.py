from pydantic import BaseModel, Field


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
