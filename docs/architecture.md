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
    LLMClient -->|Inherited By| CustomClient[Custom Enterprise Client]

    LLMClientFactory -->|Allows Registration of| CustomClient

    GitHubSummarizer[GitHubSummarizer] -->|Depends On| LLMClient
    CVOptimizer[CVOptimizer] -->|Depends On| LLMClient

    StateGraph[StateGraph] -->|Uses| BaseCheckpointer[BaseCheckpointer (Abstract)]
    StateGraph -->|Uses| RouterAgent[RouterAgent]
    RouterAgent -->|Queries| AsyncRAGPipeline[AsyncRAGPipeline]
```

## Core Abstractions

### 1. Abstract Client Class (`LLMClient`)
- Located in `src/resumesh_llm/core/clients/base.py`.
- Solves **Dependency Inversion**: High-level modules do not depend on concrete implementations like `OpenAIClient`. They only interact via the abstract `LLMClient.generate` and `generate_structured_output` interfaces.
- Solves **Liskov Substitution**: Any subclass of `LLMClient` conforms to the abstract contracts and can replace any other. Now also supports asynchronous batch operations via `generate_batch` and `generate_structured_output_batch`.

### 2. Client Factory & Pluggable Registry (`LLMClientFactory`)
- Located in `src/resumesh_llm/core/factory.py`.
- Solves **Single Responsibility**: Consolidates provider selection, credentials mapping, and parameter checking.
- **Open-Closed Principle**: Supports dynamic provider registry via `register_provider(name, client_class)`, letting developers plug in custom client architectures without modifying library source code.

### 3. Graph Checkpoint Engines (`BaseCheckpointer`)
- Located in `src/resumesh_llm/core/graph.py`.
- Enables state machine persistence to save and restore execution status after node completions:
  - `MemoryCheckpointer`: Volatile memory-backed storage.
  - `FileCheckpointer`: Disk-based JSON persistence.

### 4. Output Parsing & Strict Validation (`OutputParser`)
- Located in `src/resumesh_llm/core/clients/parser.py`.
- Enforces strict Pydantic V2 verification on all responses. If LLMs return invalid schema keys or hallucinate types, `OutputParser` raises exceptions that are caught by `retry_with_backoff` to automatically re-request the prompt.

### 5. Async RAG & Router Agent
- `AsyncRAGPipeline` (in `core/rag.py`): Ingests and queries job regulations and ATS requirements asynchronously.
- `RouterAgent` (in `core/router.py`): Examines states against retrieved chunks from the RAG pipeline using LLM reasoning to route workflows.

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
