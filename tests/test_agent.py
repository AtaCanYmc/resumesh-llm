import pytest

from resumesh_llm.core.agent import BulletRefinementAgent
from resumesh_llm.core.clients import MockClient


@pytest.mark.asyncio
async def test_bullet_refinement_agent():
    client = MockClient()
    agent = BulletRefinementAgent(client=client)

    bullets = [
        "Implemented mock provider client",
        "Configured robust tests",
    ]

    # Run the refinement agent
    refined = await agent.refine(
        drafts=bullets,
        job_description="We need a Python developer who writes tests.",
        max_iterations=1,
    )

    assert len(refined) > 0
    # The mock client returns the highlights mock JSON by default
    assert any(
        "Implemented mock provider" in b or "suite" in b or "Designed" in b
        for b in refined
    )
