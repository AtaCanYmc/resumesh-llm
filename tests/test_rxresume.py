import pytest

from resumesh_llm.core.clients import MockClient
from resumesh_llm.rxresume.optimizer import CVOptimizer


@pytest.mark.asyncio
async def test_optimize_bullet_point():
    client = MockClient()
    optimizer = CVOptimizer(client=client)

    result = await optimizer.optimize_bullet_point(
        raw_bullet="I worked on fixing bugs and writing tests",
        context="Software Engineer",
    )

    assert result.original == "I worked on fixing bugs and writing tests"
    assert result.optimized != ""
    assert result.explanation != ""


@pytest.mark.asyncio
async def test_extract_skills():
    client = MockClient()
    optimizer = CVOptimizer(client=client)

    result = await optimizer.extract_skills(
        text="Experience with Python, FastAPI, AWS, and Git. Strong Agile leader."
    )

    assert len(result.hard_skills) > 0
    assert len(result.soft_skills) > 0
    assert len(result.tools_and_platforms) > 0


@pytest.mark.asyncio
async def test_analyze_alignment():
    client = MockClient()
    optimizer = CVOptimizer(client=client)

    result = await optimizer.analyze_alignment(
        cv_text="Python software engineer with 3 years experience in backend APIs.",
        job_description="Looking for senior Python developer with Kubernetes and AWS experience.",
    )

    assert result.match_score > 0
    assert len(result.missing_skills) > 0
    assert len(result.suggestions) > 0
