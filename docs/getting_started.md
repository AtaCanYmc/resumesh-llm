# Getting Started with `resumesh-llm`

Welcome to `resumesh-llm`! This guide helps you install the package, initialize your first LLM client, and start summarizing repositories or optimizing resume contents.

## Installation

Ensure you have Python 3.10+ installed.

### Standard Installation (Development)

Clone the repository and install it in editable mode inside your virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

---

## Initializing Clients with LLMClientFactory

The client factory creates LLM clients dynamically. It checks which provider is specified and configures them accordingly.

### 1. OpenAI Provider (GPT-4o, etc.)
Requires an `api_key`.

```python
import asyncio
from resumesh_llm import LLMClientFactory, LLMRequest

async def run_openai():
    client = LLMClientFactory.get_client(
        provider="openai",
        api_key="sk-your-openai-api-key",
        model="gpt-4o"
    )
    
    resp = await client.generate(LLMRequest(prompt="Hello, who are you?"))
    print(resp.text)

asyncio.run(run_openai())
```

### 2. Groq Provider
Requires an `api_key` and is powered by fast open weights models like Llama 3.

```python
async def run_groq():
    client = LLMClientFactory.get_client(
        provider="groq",
        api_key="gsk-your-groq-api-key",
        model="llama-3.3-70b-versatile"
    )
    
    resp = await client.generate(LLMRequest(prompt="Summarize the concept of recursion."))
    print(resp.text)
```

### 3. Ollama Provider (Local LLMs)
Runs locally without API keys. Assumes Ollama is running on your machine (default port: `11434`).

```python
async def run_ollama():
    client = LLMClientFactory.get_client(
        provider="ollama",
        base_url="http://localhost:11434",
        model="llama3"
    )
    
    resp = await client.generate(LLMRequest(prompt="What is a binary search tree?"))
    print(resp.text)
```

### 4. Mock Provider (Testing / Offline)
Does not require any network access or keys. Returns a structured dummy response, respecting `response_format` configuration.

```python
async def run_mock():
    client = LLMClientFactory.get_client(provider="mock")
    resp = await client.generate(LLMRequest(prompt="This will return mock data"))
    print(resp.text)
```

---

## Configuration Reference

The request parameters inside `LLMRequest` control model behavior:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `prompt` | `str` | *Required* | The user request or instructions. |
| `system_instruction` | `str` | `None` | Developer instructions or persona guidelines. |
| `temperature` | `float` | `0.7` | Value between `0.0` (deterministic) and `2.0` (creative). |
| `max_tokens` | `int` | `None` | Stop generation once limit is reached. |
| `response_format` | `str` | `None` | Set to `"json_object"` to force JSON schemas. |
