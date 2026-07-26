from resumesh_llm.core.client import (
    GroqClient,
    LLMClient,
    MockClient,
    OllamaClient,
    OpenAIClient,
)
from resumesh_llm.core.exceptions import ConfigurationError


class LLMClientFactory:
    """Factory for instantiating the appropriate LLMClient based on the provider."""

    @staticmethod
    def get_client(
        provider: str,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ) -> LLMClient:
        """Creates and returns an instance of an LLMClient.

        Args:
            provider: The name of the provider ('openai', 'groq', 'ollama', 'mock').
            api_key: Secret API key for OpenAI or Groq.
            model: Name of the LLM model (e.g. 'gpt-4o', 'llama3').
            base_url: Optional base url for Ollama or custom OpenAI endpoints.
            kwargs: Extra parameters to pass to client initialization.

        Returns:
            An instance of LLMClient subclass.

        Raises:
            ConfigurationError: If requirements for a provider are missing.
        """
        provider_clean = provider.lower().strip()

        if provider_clean == "openai":
            model_name = model or "gpt-4o"
            if not api_key:
                raise ConfigurationError("api_key is required for 'openai' provider.")
            return OpenAIClient(
                api_key=api_key, model_name=model_name, base_url=base_url
            )

        elif provider_clean == "groq":
            model_name = model or "llama-3.3-70b-versatile"
            if not api_key:
                raise ConfigurationError("api_key is required for 'groq' provider.")
            return GroqClient(api_key=api_key, model_name=model_name)

        elif provider_clean == "ollama":
            model_name = model or "llama3"
            url = base_url or "http://localhost:11434"
            return OllamaClient(base_url=url, model_name=model_name)

        elif provider_clean == "mock":
            model_name = model or "mock-model"
            mock_response = kwargs.get("mock_response")
            return MockClient(model_name=model_name, mock_response=mock_response)

        else:
            raise ConfigurationError(
                f"Unsupported LLM provider: '{provider}'. Supported providers are: 'openai', 'groq', 'ollama', 'mock'."
            )
