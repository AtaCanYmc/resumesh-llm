import asyncio
import json

from resumesh_llm import (
    AsyncRAGPipeline,
    LLMClient,
    LLMClientFactory,
    LLMRequest,
    LLMResponse,
    MemoryCheckpointer,
    RouterAgent,
    StateGraph,
)


# 1. Define a Custom LLM Client demonstrating the Pluggable Client Registry
class CustomEnterpriseLLM(LLMClient):
    """Custom corporate internal LLM provider client."""

    def __init__(self, api_key: str, model_name: str = "enterprise-v3"):
        super().__init__(model_name)
        self.api_key = api_key

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Mocking routing response logic
        if (
            "route" in request.prompt
            or "Determine the correct next step" in request.prompt
        ):
            return LLMResponse(
                text=json.dumps({"route": "ats_optimization"}),
                usage=None,
                provider="enterprise",
                model=self.model_name,
            )
        return LLMResponse(
            text=json.dumps({"optimized": "Accomplished Z using Y as measured by X"}),
            usage=None,
            provider="enterprise",
            model=self.model_name,
        )

    async def generate_structured_output(
        self, request: LLMRequest, response_model: type
    ):
        from resumesh_llm.core.clients.parser import OutputParser

        res = await self.generate(request)
        return OutputParser.parse_and_validate(res.text, response_model)


async def main():
    print("=== Step 1: Register Custom LLM Provider Class ===")
    LLMClientFactory.register_provider("enterprise", CustomEnterpriseLLM)
    client = LLMClientFactory.get_client("enterprise", api_key="secret-enterprise-key")
    print(
        f"Registered and instantiated provider: {type(client).__name__} (Model: {client.model_name})"
    )

    print("\n=== Step 2: Build & Populate Async RAG Pipeline ===")
    rag = AsyncRAGPipeline()
    await rag.add_document(
        "ats_rules",
        "ATS formatting guidelines dictate clear section headers and no complex layouts.",
    )
    await rag.add_document(
        "compliance_rules",
        "Resume must adhere to local GDPR compliance standards when processing user info.",
    )
    print("Async RAG Pipeline populated with document chunks.")

    print("\n=== Step 3: Initialize Router Agent ===")
    router = RouterAgent(client=client, rag_pipeline=rag)
    print("Router Agent configured.")

    print("\n=== Step 4: Configure StateGraph with State Checkpointing ===")
    checkpointer = MemoryCheckpointer()
    graph = StateGraph(checkpointer=checkpointer)

    # Register workflow nodes
    async def ats_optimization_node(state):
        print("[Node: ATS Optimization] Fixing layout and header compliance...")
        state["path"].append("ats_optimization")
        return {"bullets": [b + " (ATS compliant)" for b in state["bullets"]]}

    async def standard_critique_node(state):
        print("[Node: Standard Critique] Critiquing resume bullets...")
        state["path"].append("standard_critique")
        return {}

    graph.add_node("ats_optimization", ats_optimization_node)
    graph.add_node("standard_critique", standard_critique_node)

    # Use our Router Agent directly as an asynchronous conditional router edge!
    graph.add_conditional_edge("START", router.route)

    graph.add_edge("ats_optimization", "END")
    graph.add_edge("standard_critique", "END")

    # Ensure START node exists to kick off the router
    graph.add_node("START", lambda state: {"path": ["START"]})

    # Initial state
    initial_state = {
        "bullets": ["Wrote code for a Python app"],
        "job_description": "We need an engineer who understands GDPR and ATS compliance.",
        "path": [],
    }

    print("\n=== Step 5: Execute Graph Workflow (Checkpoint run-001) ===")
    final_state = await graph.run(
        initial_state, entry_point="START", checkpoint_id="run-001"
    )
    print(f"Workflow execution path: {final_state.get('path')}")
    print(f"Final state bullets: {final_state.get('bullets')}")

    # Inspect the checkpoint saved
    checkpoint = await checkpointer.load("run-001")
    print(f"\nCheckpoint verified. Last node index state: {checkpoint[1]}")


if __name__ == "__main__":
    asyncio.run(main())
