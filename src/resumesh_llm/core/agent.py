import json
import logging
from typing import Any

from resumesh_llm.core.clients.base import LLMClient
from resumesh_llm.core.graph import StateGraph
from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class BulletRefinementAgent:
    """An LLM-based agent implementing an iterative Critique-and-Refine self-reflection loop

    using a graph-based state machine architecture (StateGraph) for deterministic routing.
    """

    def __init__(self, client: LLMClient):
        self.client = client

    async def refine(
        self,
        drafts: list[str],
        job_description: str | None = None,
        max_iterations: int = 2,
    ) -> list[str]:
        """Runs the iterative agentic self-reflection loop using StateGraph orchestration.

        Args:
            drafts: Initial list of resume bullet points.
            job_description: Optional target job description to match against.
            max_iterations: Maximum loop iterations.

        Returns:
            List of refined bullet points.
        """
        graph = StateGraph()

        # Define node functions
        async def critique_node(state: dict[str, Any]) -> dict[str, Any]:
            system_critique = PromptLoader.load_and_render(
                domain="agent", template_name="critique_system"
            )
            prompt_critique = PromptLoader.load_and_render(
                domain="agent",
                template_name="critique_user",
                bullets=state["bullets"],
                job_description=state["job_description"],
            )

            request = LLMRequest(
                prompt=prompt_critique,
                system_instruction=system_critique,
                temperature=0.3,
                response_format="json_object",
            )

            try:
                response = await self.client.generate(request)
                critique_data = json.loads(response.text)
                return {
                    "critique": critique_data.get("critique", ""),
                    "is_satisfactory": critique_data.get("is_satisfactory", True),
                    "iterations": state["iterations"] + 1,
                }
            except Exception as e:
                logger.warning(f"Critique node failure: {str(e)}")
                return {
                    "is_satisfactory": True,
                    "iterations": state["iterations"] + 1,
                }

        async def refine_node(state: dict[str, Any]) -> dict[str, Any]:
            system_refine = PromptLoader.load_and_render(
                domain="agent", template_name="refine_system"
            )
            prompt_refine = PromptLoader.load_and_render(
                domain="agent",
                template_name="refine_user",
                bullets=state["bullets"],
                critique=state["critique"],
                job_description=state["job_description"],
            )

            request_refine = LLMRequest(
                prompt=prompt_refine,
                system_instruction=system_refine,
                temperature=0.4,
                response_format="json_object",
            )

            try:
                response_refine = await self.client.generate(request_refine)
                refine_data = json.loads(response_refine.text)
                new_bullets = (
                    refine_data.get("bullet_points")
                    or refine_data.get("highlights")
                    or []
                )
                if new_bullets:
                    return {"bullets": new_bullets}
            except Exception as e:
                logger.warning(f"Refine node failure: {str(e)}")
            return {}

        # Define routing function
        def router(state: dict[str, Any]) -> str:
            if state["is_satisfactory"] or state["iterations"] >= max_iterations:
                return "END"
            return "refine"

        # Register nodes and transitions
        graph.add_node("critique", critique_node)
        graph.add_node("refine", refine_node)

        graph.add_conditional_edge("critique", router)
        graph.add_edge("refine", "critique")

        # Set initial state
        initial_state = {
            "bullets": list(drafts),
            "job_description": job_description,
            "critique": "",
            "is_satisfactory": False,
            "iterations": 0,
        }

        # Run state machine
        final_state = await graph.run(initial_state, entry_point="critique")
        return final_state["bullets"]
