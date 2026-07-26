# Architecture Overview

This document describes the architectural layout and design patterns of `resumesh-llm`. The library is designed to be highly modular, decoupled, and consistent with the **SOLID** software design principles.

## Module Relations

The library separation is visualised below:

```mermaid
graph TD
    ClientFactory[LLMClientFactory] -->|Instantiates| LLMClient[LLMClient (Abstract)]
    LLMClient -->|Inherited By| OpenAIClient[OpenAIClient]
    LLMClient -->|Inherited By| GroqClient[GroqClient]
    LLMClient -->|Inherited By| OllamaClient[OllamaClient]
    LLMClient -->|Inherited By| MockClient[MockClient]
    
    GitHubSummarizer[GitHubSummarizer] -->|Depends On| LLMClient
    CVOptimizer[CVOptimizer] -->|Depends On| LLMClient
    
    LLMRequest[LLMRequest Schema] -->|Input parameter| LLMClient
    LLMClient -->|Returns| LLMResponse[LLMResponse Schema]
```

## Core Abstractions

### 1. Abstract Client Class (`LLMClient`)
- Located in `src/resumesh_llm/core/client.py`.
- Solves **Dependency Inversion**: High-level modules (`GitHubSummarizer`, `CVOptimizer`) do not depend on concrete implementations like `OpenAIClient`. They only interact via the abstract `LLMClient.generate` interface.
- Solves **Liskov Substitution**: Any subclass of `LLMClient` conforms to the abstract `generate(request: LLMRequest) -> LLMResponse` contract and can replace any other.

### 2. Client Factory (`LLMClientFactory`)
- Located in `src/resumesh_llm/core/factory.py`.
- Solves **Single Responsibility**: Consolidates provider selection, endpoint setups, and parameter checking in one helper class.

### 3. Data Schemas
- Defined using `pydantic` in `src/resumesh_llm/core/models.py`.
- Respects **Interface Segregation**: Splits inputs (`LLMRequest`) and outputs (`LLMResponse`) cleanly, omitting unnecessary data bloat.

---

## Error Handling Design

Custom exceptions are categorized under `src/resumesh_llm/core/exceptions.py`:

```mermaid
graph TD
    Exception[Exception] --> LLMError[LLMError (Base)]
    LLMError --> ConfigurationError[ConfigurationError]
    LLMError --> ProviderError[ProviderError]
    ProviderError --> RateLimitError[RateLimitError (429)]
```

- **`ConfigurationError`**: Raised during client validation if credentials or URLs are missing.
- **`ProviderError`**: Raised if a model endpoint fails to process requests or throws HTTP errors.
- **`RateLimitError`**: A specific sub-class of `ProviderError` raised when rate limits are exhausted.
