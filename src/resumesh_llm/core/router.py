import json
import logging
from typing import Any

from resumesh_llm.core.clients.base import LLMClient
from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.rag import AsyncRAGPipeline

logger = logging.getLogger(__name__)


class RouterAgent:
    """A dynamic Router Agent that uses retrieved RAG documents (ATS guidelines, regulations)

    and LLM analysis to route a resume optimization workflow asynchronously.
    """

    def __init__(self, client: LLMClient, rag_pipeline: AsyncRAGPipeline):
        self.client = client
        self.rag_pipeline = rag_pipeline

    async def route(self, state: dict[str, Any]) -> str:
        """Asynchronously routes the state graph execution to the correct node based on inputs."""
        bullets = state.get("bullets", [])
        job_description = state.get("job_description", "")
        bullets_text = " ".join(bullets)

        # 1. Asynchronously retrieve regulations / ATS rules from the RAG pipeline
        retrieved_chunks = await self.rag_pipeline.retrieve(
            query=f"{job_description} {bullets_text}", top_k=3
        )

        # Format rules for prompt
        rules_context = "\n".join([f"- {chunk['text']}" for chunk in retrieved_chunks])

        system_instruction = (
            "You are a professional recruiting coordinator and ATS routing agent. "
            "Your task is to analyze target job details, resume content, and specific "
            "regulations/ATS requirements, and route the workflow to the correct next step. "
            "Respond ONLY with a JSON object containing the key 'route' and a string value."
        )

        prompt = (
            f"Resume draft content:\n{bullets_text}\n\n"
            f"Job Description context:\n{job_description}\n\n"
            f"Relevant Regulations & ATS Guidelines retrieved:\n{rules_context}\n\n"
            f"Determine the correct next step in the pipeline. "
            f"Choose one of the following route strings:\n"
            f"- 'ats_optimization': If the resume lacks formatting/keywords specified in the ATS guidelines.\n"
            f"- 'regulatory_alignment': If the resume violates or lacks required regulatory statements/skills (e.g. GDPR, security clearances).\n"
            f"- 'standard_critique': If no specific ATS rules or regulations are flagged, but general refinement is needed.\n"
            f"- 'END': If the resume is already optimal or no improvements are needed.\n\n"
            f'Return JSON format: {{"route": "<chosen_route>"}}'
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.1,
            response_format="json_object",
        )

        try:
            response = await self.client.generate(request)
            data = json.loads(response.text)
            route_decision = data.get("route", "standard_critique")
            logger.info(f"RouterAgent: routed workflow to '{route_decision}'")
            return route_decision
        except Exception as e:
            logger.warning(
                f"RouterAgent error: {str(e)}. Falling back to 'standard_critique'"
            )
            return "standard_critique"
