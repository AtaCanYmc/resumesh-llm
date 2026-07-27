import json
import logging

from resumesh_llm.core.client import LLMClient
from resumesh_llm.core.models import LLMRequest
from resumesh_llm.core.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class BulletRefinementAgent:
    """An LLM-based agent implementing an iterative Critique-and-Refine self-reflection loop.

    Allows optimizing resume bullets or GitHub commit logs, critiquing draft outputs against
    specific criteria and target job description keywords, and refining them dynamically.
    """

    def __init__(self, client: LLMClient):
        self.client = client

    async def refine(
        self,
        drafts: list[str],
        job_description: str | None = None,
        max_iterations: int = 2,
    ) -> list[str]:
        """Runs the iterative agentic self-reflection loop on resume bullets.

        Args:
            drafts: Initial list of resume bullet points.
            job_description: Optional target job description to match against.
            max_iterations: Maximum loop iterations.

        Returns:
            List of refined bullet points.
        """
        current_bullets = list(drafts)

        for iteration in range(1, max_iterations + 1):
            logger.info(f"Agentic loop iteration {iteration}/{max_iterations}")

            # 1. Critique
            system_critique = PromptLoader.load_and_render(
                domain="agent", template_name="critique_system"
            )
            prompt_critique = PromptLoader.load_and_render(
                domain="agent",
                template_name="critique_user",
                bullets=current_bullets,
                job_description=job_description,
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

                is_satisfactory = critique_data.get("is_satisfactory", True)
                critique_comments = critique_data.get("critique", "")

                logger.debug(
                    f"Critique: satisfactory={is_satisfactory}, comments={critique_comments}"
                )

                if is_satisfactory:
                    logger.info(
                        "Critique satisfied. Terminating refinement loop early."
                    )
                    break
            except Exception as e:
                logger.warning(
                    f"Failed to generate/parse critique: {str(e)}. Fallback to early exit."
                )
                break

            # 2. Refinement
            system_refine = PromptLoader.load_and_render(
                domain="agent", template_name="refine_system"
            )
            prompt_refine = PromptLoader.load_and_render(
                domain="agent",
                template_name="refine_user",
                bullets=current_bullets,
                critique=critique_comments,
                job_description=job_description,
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
                    current_bullets = new_bullets
            except Exception as e:
                logger.warning(
                    f"Failed to refine bullets in iteration {iteration}: {str(e)}"
                )
                break

        return current_bullets
