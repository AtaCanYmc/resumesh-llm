# resumesh-llm

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=for-the-badge&logo=python" alt="Python Versions" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT" />
  <img src="https://img.shields.io/badge/Ruff-Compliant-black?style=for-the-badge" alt="Ruff Compliant" />
  <img src="https://img.shields.io/badge/Release--Please-Enabled-orange?style=for-the-badge" alt="Release-Please Enabled" />
  <img src="https://img.shields.io/badge/Production--Ready-Yes-brightgreen?style=for-the-badge" alt="Production Ready" />
</p>

A professional-grade, lightweight, and production-ready Python library powering the intelligent LLM features of the **ResuMesh** portfolio and CV builder. Architected strictly on **SOLID** and **Domain-Driven Design (DDD)** principles, it provides robust, schema-validated, and provider-agnostic abstractions to analyze repositories, optimize resume metrics, and build active career journals.

---

## 🎯 The "Aha!" Moment: See it in Action

High-impact resumes need metrics, actions, and structure. Here is how `resumesh-llm` transforms weak descriptions into Google-style **XYZ Formula** (Accomplished [X], as measured by [Y], by doing [Z]) statements:

| Before (Weak & Passive) | After `resumesh-llm` (ATS-Optimized & Action-Oriented) |
| :--- | :--- |
| "I was responsible for fixing database bugs." | **"Optimized database query performance by 45%** (Y) by redesigning indexes and implementing Redis caching (Z) to resolve latency bottlenecks." |
| "I worked on writing unit tests for our APIs." | **"Designed and executed a robust unit testing suite, achieving 95% branch coverage** (Y) using Pytest and mock clients, ensuring CI/CD reliability." |
| "I built some features on the React frontend." | **"Spearheaded the migration of legacy client pages to Vite and React** (Z), decreasing first-contentful paint by 1.2s (Y)." |

---

## 🌟 Flagship Features

*   **🧠 Self-Reflecting Critique Agents**: Implements a graph-based state machine (`StateGraph`) that orchestrates a multi-step agentic reflection loop to refine work history.
*   **🚀 Asynchronous RAG Pipeline**: Ingests compliance regulations and ATS formatting guidelines, retrieving relevant chunks on the fly without blocking execution.
*   **📊 Dynamic Gap Analysis**: Gamifies CV-to-Job alignment, detecting missing hard/soft skills and offering suggestions.
*   **💾 State Graph Checkpointing**: Built-in Memory and Disk checkpointers (`MemoryCheckpointer` / `FileCheckpointer`) to freeze state and resume execution if rate limits or API outages occur.
*   **🔌 Pluggable Provider Registry**: Out-of-the-box support for OpenAI, Groq, Ollama, and Mock clients. Extend or inject custom proprietary LLM models dynamically.
*   **🔒 Strict Pydantic V2 Validation**: Uses a dedicated `OutputParser` layer to ensure LLM outputs conform exactly to models, triggering auto-retries on validation errors.

---

## ⚡ Frictionless Quickstart

Get up and running in under 60 seconds.

### Step 1: Install the Package
```bash
pip install -e .
```

### Step 2: Configure API Key (Optional)
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Step 3: Run the Code
```python
import asyncio
from resumesh_llm import LLMClientFactory, CVOptimizer

async def main():
    # Initialize the client (uses MockClient offline by default)
    client = LLMClientFactory.get_client(provider="mock")
    optimizer = CVOptimizer(client=client)

    # Optimize experience using the Google XYZ formula
    result = await optimizer.optimize_bullet_point(
        raw_bullet="I worked on fixing bugs and writing tests",
        context="Backend Developer"
    )

    print(f"Original: {result.original}")
    print(f"Optimized: {result.optimized}")
    print(f"Rationale: {result.explanation}")

asyncio.run(main())
```

---

## 🛠️ Architecture & Workflow Pipeline

We partition domains cleanly using the **Facade Pattern** to export simplified entry points, avoiding circular imports.

### Agentic Workflow & Checkpoint Pipeline

```mermaid
graph TD
    User([Client Application]) -->|Triggers run| StateGraph[StateGraph Orchestrator]
    StateGraph -->|Loads Checkpoint| Checkpointer[(BaseCheckpointer)]
    StateGraph -->|Invokes| RouterAgent[RouterAgent]
    RouterAgent -->|Queries| RAG[AsyncRAGPipeline]
    RAG -.->|Retrieves Chunks| Regulations[(Regulations & ATS Guidelines)]
    RouterAgent -->|Decides route| Decision{Routing Decision}
    Decision -->|ats_optimization| ATSNode[ATS Optimization Node]
    Decision -->|regulatory_alignment| RegNode[Regulatory Alignment Node]
    Decision -->|standard_critique| CritiqueNode[Standard Critique Node]
    ATSNode -->|Updates State| Save[Save Checkpoint]
    RegNode -->|Updates State| Save
    CritiqueNode -->|Updates State| Save
    Save -->|Persists state & pointer| Checkpointer
```

---

## 📚 Documentation Map

Delve deeper into the architecture and subdomains of `resumesh-llm`:

*   📖 **[Getting Started Guide](docs/getting_started.md)**: Configuration reference, environment setup, and registering custom LLM providers.
*   📐 **[Architecture Overview](docs/architecture.md)**: Detailed SOLID design patterns, class structures, and exception hierarchies.
*   ✏️ **[CV Optimizer Reference](docs/cv_optimizer.md)**: XYZ formulations, skill classifiers, and job description alignment analyzer.
*   🐙 **[GitHub Summarizer Reference](docs/github_summarizer.md)**: Scraped commit processing, career journals, and repository summarization.
*   🧪 **[Testing Documentation](docs/testing.md)**: Local testing, mock provider verification, and formatting commands.

---

## 🤝 Community & Contributing

We welcome issues, feedback, and pull requests! Please read our **[Contributing Guide](CONTRIBUTING.md)** and **[Code of Conduct](CODE_OF_CONDUCT.md)** to get started.

If you find `resumesh-llm` useful or are using it to build your developer portfolio, support us by leaving a star! ⭐️

<p align="center">
  <b>resumesh-llm</b> is maintained by the ResuMesh Team.
</p>
