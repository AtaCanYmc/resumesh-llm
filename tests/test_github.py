from datetime import datetime

import pytest

from resumesh_llm.core.clients import MockClient
from resumesh_llm.github.summarizer import (
    GitHubCommitModel,
    GitHubRepoInput,
    GitHubSummarizer,
)


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


@pytest.mark.asyncio
async def test_generate_journal_bullets():
    client = MockClient()
    summarizer = GitHubSummarizer(client=client)

    bullets = await summarizer.generate_journal_bullets(
        repo_name="AwesomeProject",
        commits=["feat: added endpoints", "fix: corrected schemas"],
    )

    assert len(bullets) > 0
    assert any("test" in b or "Designed" in b for b in bullets)


@pytest.mark.asyncio
async def test_generate_journal_bullets_with_models():
    client = MockClient()
    summarizer = GitHubSummarizer(client=client)

    commits = [
        GitHubCommitModel(
            sha="sha1",
            message="feat: added endpoints",
            author_name="Alice",
            author_email="alice@example.com",
            date=datetime.now(),
            repo_name="AwesomeProject",
            repo_full_name="owner/AwesomeProject",
            html_url="https://github.com/owner/AwesomeProject/commit/sha1",
        ),
        GitHubCommitModel(
            sha="sha2",
            message="fix: corrected schemas",
            author_name="Alice",
            author_email="alice@example.com",
            date=datetime.now(),
            repo_name="AwesomeProject",
            repo_full_name="owner/AwesomeProject",
            html_url="https://github.com/owner/AwesomeProject/commit/sha2",
        ),
    ]

    bullets = await summarizer.generate_journal_bullets(
        repo_name="AwesomeProject",
        commits=commits,
    )

    assert len(bullets) > 0
    assert any("test" in b or "Designed" in b for b in bullets)
