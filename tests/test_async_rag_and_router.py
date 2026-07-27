import json

import pytest

from resumesh_llm.core.clients import MockClient
from resumesh_llm.core.graph import StateGraph
from resumesh_llm.core.rag import AsyncRAGPipeline
from resumesh_llm.core.router import RouterAgent


@pytest.mark.asyncio
async def test_async_rag_pipeline():
    pipeline = AsyncRAGPipeline(chunk_size=10, chunk_overlap=2)

    # Ingest document
    doc_content = "This is a simple document about ATS formatting guidelines. Resumes should use chronological order."
    await pipeline.add_document("doc1", doc_content, {"category": "ATS"})

    assert len(pipeline.chunks) > 0

    # Retrieve chunks
    results = await pipeline.retrieve("chronological ATS", top_k=2)
    assert len(results) > 0
    assert "ATS" in results[0]["text"] or "chronological" in results[0]["text"]
    assert results[0]["metadata"]["category"] == "ATS"


@pytest.mark.asyncio
async def test_state_graph_async_nodes_and_routers():
    graph = StateGraph()

    # Register async nodes
    async def node_a(state):
        state["path"].append("A")
        return {"val": 1}

    async def node_b(state):
        state["path"].append("B")
        return {"val": 2}

    # Register async router
    async def route_fn(state):
        if state["val"] == 1:
            return "node_b"
        return "END"

    graph.add_node("node_a", node_a)
    graph.add_node("node_b", node_b)
    graph.add_conditional_edge("node_a", route_fn)
    graph.add_edge("node_b", "END")

    initial_state = {"path": [], "val": 0}
    final_state = await graph.run(initial_state, "node_a")

    assert final_state["path"] == ["A", "B"]
    assert final_state["val"] == 2


@pytest.mark.asyncio
async def test_router_agent_decisions():
    pipeline = AsyncRAGPipeline()
    await pipeline.add_document("doc1", "ATS guideline formatting compliance")

    # Mock LLM Client that responds with route decision
    mock_resp = json.dumps({"route": "ats_optimization"})
    client = MockClient(mock_response=mock_resp)

    router = RouterAgent(client=client, rag_pipeline=pipeline)

    state = {
        "bullets": ["Wrote code for a Python app"],
        "job_description": "We need a Python developer who follows ATS guidelines.",
    }

    decision = await router.route(state)
    assert decision == "ats_optimization"
