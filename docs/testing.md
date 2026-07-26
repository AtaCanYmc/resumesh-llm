# Testing Handbook

`resumesh-llm` comes equipped with a comprehensive test suite to verify code correctness without generating API bills or requiring active internet access.

## Running Tests

Tests are executed with `pytest` inside the virtual environment.

```bash
# Ensure you are in the root directory
cd resumesh-llm

# Activate virtual environment
source .venv/bin/activate

# Execute pytest with path configuration
PYTHONPATH=src pytest
```

---

## Mocking and Offline Execution

Tests use the built-in `MockClient` (instead of calling OpenAI/Groq endpoints). This achieves several benefits:
1. **Speed**: Run tests in under 1 second.
2. **Cost**: Zero API token expenses.
3. **Consistency**: Prevent rate-limits or network failures from breaking CI pipelines.

### How MockClient is Utilized in Tests

When writing tests for services like `CVOptimizer`, we instantiate the service using `MockClient` instead of standard providers:

```python
import pytest
from resumesh_llm import MockClient, CVOptimizer

@pytest.mark.asyncio
async def test_my_service():
    # Instantiate MockClient
    client = MockClient(model_name="mock-model")
    
    # Inject it into service
    optimizer = CVOptimizer(client=client)
    
    # Run assertions
    result = await optimizer.optimize_bullet_point("wrote tests")
    assert result.original == "wrote tests"
    assert len(result.optimized) > 0
```
