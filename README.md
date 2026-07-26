# resumesh-llm

[![CI Pipeline](https://github.com/AtaCanYmc/resumesh-llm/actions/workflows/ci.yml/badge.svg)](https://github.com/AtaCanYmc/resumesh-llm/actions/workflows/ci.yml)

A lightweight, production-ready Python library implementing the LLM integration features for the **ResuMesh** CV and portfolio builder. Designed following **KISS** (Keep It Simple, Stupid) and **SOLID** principles, `resumesh-llm` provides robust, schema-validated, and providers-agnostic abstractions to summarize projects and optimize resumes.

---

## Features

- **Multi-Provider LLM Clients**: Unified interface supporting OpenAI, Groq, local Ollama servers, and a built-in Mock provider (for CI/CD and offline development).
- **SOLID Architecture**: Low coupling, high cohesion, dependency inversion via abstract interfaces, and single responsibility separation.
- **GitHub Repository Analysis**: Extracts raw metadata and README descriptions to generate resume-ready summaries, technical tag keywords, and developer highlights.
- **CV/Resume Optimization**: 
  - **Bullet Point Optimizer**: Refactors bullet points based on the Google XYZ formula: *Accomplished [X] as measured by [Y], by doing [Z]*.
  - **Skill Extractor**: Automatically parses hard, soft, and tool/platform skills from text.
  - **ATS Alignment Matcher**: Matches resume contents with job descriptions, offering detailed keyword overlap scores and improvement suggestions.

---

## Directory Layout

```text
resumesh-llm/
├── pyproject.toml              # Build backend and dependencies
├── requirements.txt            # Dev package versions
├── README.md                   # Documentation
├── src/
│   └── resumesh_llm/
│       ├── __init__.py         # Package entry points
│       ├── core/               # LLM abstraction and providers
│       │   ├── __init__.py
│       │   ├── exceptions.py   # Standardized errors
│       │   ├── models.py       # Pydantic schemas (Request / Response)
│       │   ├── client.py       # Abstract Base Client and concrete classes
│       │   └── factory.py      # LLMClientFactory instantiation helper
│       ├── github/             # GitHub analysis logic
│       │   ├── __init__.py
│       │   └── summarizer.py   # GitHubSummarizer
│       └── rxresume/           # Resume optimization logic
│           ├── __init__.py
│           └── optimizer.py    # CVOptimizer
└── tests/                      # Pytest suite
```

---

## Design Principles

### KISS (Keep It Simple, Stupid)
- Avoids over-engineering. No complex langchain wrappers or heavy agent frameworks.
- Relies on native SDKs (`openai`) and simple HTTP requests (`httpx`) to call models.
- Standardized inputs and outputs are validated via basic Pydantic models.

### SOLID
- **Single Responsibility**: `GitHubSummarizer` does not know how to connect to OpenAI; it only knows how to build repository prompts. `LLMClient` does not know about GitHub structures.
- **Open/Closed**: Adding a new provider (e.g. Anthropic/Claude) only requires creating a new client class inheriting from `LLMClient`. No modification is needed in the services.
- **Liskov Substitution**: Any concrete client (e.g. `OllamaClient`, `MockClient`) can be passed wherever `LLMClient` is expected.
- **Interface Segregation**: Clean, minimal client definitions.
- **Dependency Inversion**: Services (`GitHubSummarizer`, `CVOptimizer`) depend on the abstract `LLMClient`, not concrete client classes.

---

## Installation

To install dependencies locally for development or testing:

```bash
pip install -r requirements.txt
# Or install in editable mode
pip install -e .
```

---

## Quick Start & Usage Examples

### 1. Basic Generation with Factory

```python
import asyncio
from resumesh_llm import LLMClientFactory, LLMRequest

async def main():
    # Instantiate client dynamically via factory
    client = LLMClientFactory.get_client(
        provider="openai",
        api_key="your-openai-api-key",
        model="gpt-4o"
    )

    request = LLMRequest(
        prompt="Tell me the benefit of SOLID principles in 1 sentence.",
        temperature=0.3
    )

    response = await client.generate(request)
    print(f"Generated text: {response.text}")
    print(f"Tokens Used: {response.usage.total_tokens if response.usage else 'N/A'}")

asyncio.run(main())
```

### 2. Summarize a GitHub Repository

```python
from resumesh_llm import LLMClientFactory, GitHubSummarizer, GitHubRepoInput

async def main():
    client = LLMClientFactory.get_client(provider="mock")
    summarizer = GitHubSummarizer(client=client)

    repo_input = GitHubRepoInput(
        repo_name="FastAPI-eCommerce",
        description="A backend commerce application built with FastAPI, PostgreSQL, and Redis.",
        readme_content="...",
        languages=["Python", "SQL"],
        stars=42
    )

    result = await summarizer.summarize_repo(repo_input)
    print("Summary:", result.summary)
    print("Tags:", result.tags)
    print("Highlights:", result.highlights)

import asyncio
asyncio.run(main())
```

### 3. CV Bullet Point Optimization

```python
from resumesh_llm import LLMClientFactory, CVOptimizer

async def main():
    client = LLMClientFactory.get_client(provider="mock")
    optimizer = CVOptimizer(client=client)

    raw_bullet = "I worked on fixing bugs and writing tests"
    result = await optimizer.optimize_bullet_point(raw_bullet, context="Backend Developer")
    
    print("Original:", result.original)
    print("Optimized:", result.optimized)
    print("Reasoning:", result.explanation)

import asyncio
asyncio.run(main())
```

---

## Testing & CI/CD

### Local Testing
Run tests using `pytest` (which uses `pytest-asyncio` for async tests and mocks all API requests):

```bash
# Explicitly set pythonpath to src and run pytest
PYTHONPATH=src pytest
```

### CI/CD Pipeline
Continuous Integration is configured via **GitHub Actions** in [.github/workflows/ci.yml](file:///.github/workflows/ci.yml):
- **Triggers**: Executes on pull requests and pushes to `main`, `master`, and `develop` branches.
- **Python Matrix**: Tests on Python `3.10`, `3.11`, and `3.12`.
- **Linting & Formatting Checks**: Runs `black` to check code formatting and `ruff` to ensure compliance with styling guidelines.
- **Automated Tests**: Executes the complete unit test suite automatically.

