import pytest
from resumesh_llm.core.client import MockClient
from resumesh_llm.github.summarizer import GitHubRepoInput, GitHubSummarizer


@pytest.mark.asyncio
async def test_github_summarizer():
    # Setup MockClient to return valid JSON
    client = MockClient(model_name="mock-model")
    summarizer = GitHubSummarizer(client=client)

    repo = GitHubRepoInput(
        repo_name="AwesomeProject",
        description="A cool python application",
        readme_content="# AwesomeProject\nThis is a cool application using FastAPI and Docker.",
        languages=["Python", "HTML"],
        stars=10,
        forks=2,
    )

    summary_result = await summarizer.summarize_repo(repo)

    assert summary_result.summary != ""
    assert "FastAPI" in summary_result.languages or "Python" in summary_result.languages
    assert len(summary_result.tags) > 0
    assert len(summary_result.highlights) > 0
