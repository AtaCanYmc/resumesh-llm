import inspect

from resumesh_llm.core.clients import (
    GroqClient,
    LLMClient,
    MockClient,
    OllamaClient,
    OpenAIClient,
)
from resumesh_llm.core.exceptions import ConfigurationError


class LLMClientFactory:
    """Factory and registry for instantiating the appropriate LLMClient based on the provider."""

    _registry: dict[str, type[LLMClient]] = {
        "openai": OpenAIClient,
        "groq": GroqClient,
        "ollama": OllamaClient,
        "mock": MockClient,
    }

    @classmethod
    def register_provider(
        cls, provider_name: str, client_class: type[LLMClient]
    ) -> None:
        """Registers a custom LLM client class for a provider name.

        Allows external developers to plug in custom LLM client implementations.

        Args:
            provider_name: Clean identifier for the provider (e.g. 'custom-cloud').
            client_class: LLMClient subclass.
        """
        provider_clean = provider_name.lower().strip()
        cls._registry[provider_clean] = client_class

    @classmethod
    def _resolve_model(cls, provider_clean: str, model: str | None) -> str:
        """Resolves the default model name for a provider if not specified."""
        default_models = {
            "openai": "gpt-4o",
            "groq": "llama-3.3-70b-versatile",
            "ollama": "llama3",
            "mock": "mock-model",
        }
        return model or default_models.get(provider_clean, "custom-model")

    @classmethod
    def _map_parameters(
        cls,
        client_cls: type[LLMClient],
        provider_clean: str,
        api_key: str | None,
        resolved_model: str,
        base_url: str | None,
        kwargs: dict,
    ) -> dict:
        """Maps parameters matching client constructor signature dynamically."""
        sig = inspect.signature(client_cls.__init__)
        params = sig.parameters

        init_kwargs = {}

        if "api_key" in params:
            init_kwargs["api_key"] = api_key or ""

        if "model_name" in params:
            init_kwargs["model_name"] = resolved_model
        elif "model" in params:
            init_kwargs["model"] = resolved_model

        if "base_url" in params:
            if base_url is not None:
                init_kwargs["base_url"] = base_url
            elif provider_clean == "ollama":
                init_kwargs["base_url"] = "http://localhost:11434"

        if "mock_response" in params and "mock_response" in kwargs:
            init_kwargs["mock_response"] = kwargs["mock_response"]

        # Map remaining custom args
        for key, value in kwargs.items():
            if key in params:
                init_kwargs[key] = value

        return init_kwargs

    @classmethod
    def get_client(
        cls,
        provider: str,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ) -> LLMClient:
        """Creates and returns an instance of an LLMClient.

        Args:
            provider: The name of the provider ('openai', 'groq', 'ollama', 'mock' or custom registered).
            api_key: Secret API key for OpenAI or Groq.
            model: Name of the LLM model (e.g. 'gpt-4o', 'llama3').
            base_url: Optional base url for Ollama or custom OpenAI endpoints.
            kwargs: Extra parameters to pass to client initialization.

        Returns:
            An instance of LLMClient subclass.

        Raises:
            ConfigurationError: If requirements for a provider are missing or provider unsupported.
        """
        provider_clean = provider.lower().strip()

        if provider_clean not in cls._registry:
            raise ConfigurationError(
                f"Unsupported LLM provider: '{provider}'. "
                f"Registered providers are: {list(cls._registry.keys())}."
            )

        client_cls = cls._registry[provider_clean]
        resolved_model = cls._resolve_model(provider_clean, model)
        init_kwargs = cls._map_parameters(
            client_cls, provider_clean, api_key, resolved_model, base_url, kwargs
        )

        try:
            return client_cls(**init_kwargs)
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                f"Failed to instantiate client for provider '{provider}': {str(e)}"
            ) from e
