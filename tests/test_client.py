import pytest

from resumesh_llm.core.clients import MockClient, OpenAIClient
from resumesh_llm.core.exceptions import ConfigurationError
from resumesh_llm.core.factory import LLMClientFactory
from resumesh_llm.core.models import LLMRequest


@pytest.mark.asyncio
async def test_mock_client_generation():
    client = MockClient(model_name="test-mock")
    req = LLMRequest(prompt="Hello, this is a test prompt")

    resp = await client.generate(req)

    assert resp.provider == "mock"
    assert resp.model == "test-mock"
    assert "Mocked response for prompt" in resp.text
    assert resp.usage is not None
    assert resp.usage.total_tokens == 25


@pytest.mark.asyncio
async def test_mock_client_json_format():
    client = MockClient(model_name="test-mock")
    req = LLMRequest(prompt="Please return JSON", response_format="json_object")

    resp = await client.generate(req)

    assert resp.provider == "mock"
    assert "mock" in resp.text  # it returns mocked JSON containing "mock"


def test_factory_creation():
    client = LLMClientFactory.get_client("mock", model="custom-mock")
    assert isinstance(client, MockClient)
    assert client.model_name == "custom-mock"

    with pytest.raises(ConfigurationError):
        LLMClientFactory.get_client("openai", api_key="")

    with pytest.raises(ConfigurationError):
        LLMClientFactory.get_client("unsupported-provider")


@pytest.mark.asyncio
async def test_openai_missing_key():
    with pytest.raises(ConfigurationError):
        OpenAIClient(api_key="")
