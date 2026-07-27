import asyncio
import os
from datetime import datetime

from resumesh_llm import GitHubCommitModel, GitHubSummarizer, LLMClientFactory


async def main():
    print("--- 03. GitHub Journal Commits to Bullets Example ---")

    provider = os.getenv("LLM_PROVIDER", "mock")
    client = LLMClientFactory.get_client(
        provider=provider, api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )
    summarizer = GitHubSummarizer(client=client)

    # Commits scraper model representation
    commits = [
        GitHubCommitModel(
            sha="c1b2a3",
            message="feat: added async state graph engine for agents",
            author_name="Alice Dev",
            author_email="alice@example.com",
            date=datetime.now(),
            repo_name="resumesh-llm",
            repo_full_name="owner/resumesh-llm",
            html_url="https://github.com/owner/resumesh-llm/commit/c1b2a3",
        ),
        GitHubCommitModel(
            sha="d4e5f6",
            message="fix: resolved memory leak on heavy batches",
            author_name="Alice Dev",
            author_email="alice@example.com",
            date=datetime.now(),
            repo_name="resumesh-llm",
            repo_full_name="owner/resumesh-llm",
            html_url="https://github.com/owner/resumesh-llm/commit/d4e5f6",
        ),
    ]

    print(
        "Commit History Logs (Models):\n"
        + "\n".join(f" - {c.message} ({c.sha})" for c in commits)
    )

    bullets = await summarizer.generate_journal_bullets(
        repo_name="resumesh-llm", commits=commits
    )

    print("\n--- Polished Impact Bullet Points ---")
    for idx, bullet in enumerate(bullets, 1):
        print(f"{idx}. {bullet}")


if __name__ == "__main__":
    asyncio.run(main())
