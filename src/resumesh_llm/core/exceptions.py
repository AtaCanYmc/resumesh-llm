class LLMError(Exception):
    """Base exception class for all resumesh-llm errors."""

    pass


class ConfigurationError(LLMError):
    """Raised when the LLM client or provider is misconfigured."""

    pass


class ProviderError(LLMError):
    """Raised when the LLM provider returns an API error."""

    def __init__(self, message: str, provider: str, status_code: int | None = None):
        super().__init__(
            f"[{provider.upper()} Error] {message} (Status: {status_code})"
        )
        self.provider = provider
        self.status_code = status_code


class RateLimitError(ProviderError):
    """Raised when request rate limits are exceeded."""

    def __init__(self, message: str, provider: str):
        super().__init__(message, provider, status_code=429)
