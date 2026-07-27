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
