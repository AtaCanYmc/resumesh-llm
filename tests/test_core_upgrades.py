import json
import os
import shutil
from typing import Any

import pytest
from pydantic import BaseModel, Field

from resumesh_llm.core import (
    FileCheckpointer,
    LLMClient,
    LLMClientFactory,
    LLMRequest,
    LLMResponse,
    MemoryCheckpointer,
    StateGraph,
)


# Test 1: Pydantic V2 Strict Validation & Output Parser Retry
class StrictTestModel(BaseModel):
    strict_score: int = Field(description="Must be integer")
    name: str = Field(description="Must be string")


@pytest.mark.asyncio
async def test_strict_schema_validation_and_retry():
    calls = 0

    class TemporaryFailClient(LLMClient):
        async def generate(self, request: LLMRequest) -> LLMResponse:
            nonlocal calls
            calls += 1
            if calls == 1:
                # Returns invalid types (string instead of int, and missing field)
                bad_json = json.dumps({"strict_score": "not_an_int"})
                return LLMResponse(
                    text=bad_json, usage=None, provider="temp", model="temp"
                )
            else:
                # Correct structure
                good_json = json.dumps({"strict_score": 95, "name": "Success"})
                return LLMResponse(
                    text=good_json, usage=None, provider="temp", model="temp"
                )

        async def generate_structured_output(
            self, request: LLMRequest, response_model: type
        ) -> Any:
            from resumesh_llm.core.clients.parser import OutputParser
            from resumesh_llm.core.clients.retry import retry_with_backoff

            async def _call():
                res = await self.generate(request)
                return OutputParser.parse_and_validate(res.text, response_model)

            return await retry_with_backoff(_call, retries=2, initial_delay=0.01)

    client = TemporaryFailClient("temp")
    result = await client.generate_structured_output(
        LLMRequest(prompt="Test prompt"), StrictTestModel
    )

    assert result.strict_score == 95
    assert result.name == "Success"
    assert calls == 2


# Test 2: State Graph Checkpointing (Save/Resume)
@pytest.mark.asyncio
async def test_state_graph_checkpointing_resume():
    checkpointer = MemoryCheckpointer()
    graph = StateGraph(checkpointer=checkpointer)

    node_a_calls = 0
    node_b_calls = 0

    async def node_a(state):
        nonlocal node_a_calls
        node_a_calls += 1
        return {"step_a": True}

    async def node_b(state):
        nonlocal node_b_calls
        node_b_calls += 1
        if "step_b_allowed" not in state:
            raise ValueError("Node B failed intentionally")
        return {"step_b": True}

    graph.add_node("A", node_a)
    graph.add_node("B", node_b)

    graph.add_edge("A", "B")
    graph.add_edge("B", "END")

    # Initial Run (Should execute A, checkpoint, then fail in B)
    state = {"path": []}
    with pytest.raises(ValueError, match="Node B failed intentionally"):
        await graph.run(state, entry_point="A", checkpoint_id="run-123")

    assert node_a_calls == 1
    assert node_b_calls == 1

    # Verify that checkpoint shows the graph pointer is currently at node B
    checkpoint = await checkpointer.load("run-123")
    assert checkpoint is not None
    saved_state, current_node = checkpoint
    assert saved_state["step_a"] is True
    assert current_node == "B"

    # Fix execution criteria (simulate user repairing state or resuming with extra parameters)
    saved_state["step_b_allowed"] = True
    await checkpointer.save("run-123", saved_state, "B")

    # Resume graph run (Should skip A entirely and continue from B)
    final_state = await graph.run({}, entry_point="A", checkpoint_id="run-123")

    assert node_a_calls == 1  # Node A was not re-executed
    assert node_b_calls == 2  # Node B was executed again and succeeded
    assert final_state["step_a"] is True
    assert final_state["step_b"] is True


# Test 3: FileCheckpointer save & load
@pytest.mark.asyncio
async def test_file_checkpointer():
    dir_path = ".test_checkpoints"
    checkpointer = FileCheckpointer(directory=dir_path)

    state = {"score": 100, "user": "test-user"}
    await checkpointer.save("test-chk", state, "node_c")

    loaded = await checkpointer.load("test-chk")
    assert loaded is not None
    loaded_state, current_node = loaded
    assert loaded_state == state
    assert current_node == "node_c"

    # Clean up test checkpoint directory
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


# Test 4: Pluggable Client Registry
def test_pluggable_client_registry():
    class CustomEnterpriseClient(LLMClient):
        def __init__(self, api_key: str, model_name: str = "enterprise-v1"):
            super().__init__(model_name)
            self.api_key = api_key

        async def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                text="Custom", usage=None, provider="custom", model=self.model_name
            )

        async def generate_structured_output(
            self, request: LLMRequest, response_model: type
        ) -> Any:
            pass

    # Register Custom Provider
    LLMClientFactory.register_provider("enterprise", CustomEnterpriseClient)

    # Instantiate
    client = LLMClientFactory.get_client(
        "enterprise", api_key="secret-key", model="enterprise-v2"
    )
    assert isinstance(client, CustomEnterpriseClient)
    assert client.api_key == "secret-key"
    assert client.model_name == "enterprise-v2"
