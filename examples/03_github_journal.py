import asyncio
import os

from resumesh_llm import GitHubSummarizer, LLMClientFactory


async def main():
    print("--- 03. GitHub Journal Commits to Bullets Example ---")

    provider = os.getenv("LLM_PROVIDER", "mock")
    client = LLMClientFactory.get_client(
        provider=provider, api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )
    summarizer = GitHubSummarizer(client=client)

    commits = [
        "feat: added async state graph engine for agents",
        "fix: resolved memory leak on heavy batches",
        "docs: wrote 3-step quickstart in README.md",
    ]
    print("Commit History Logs:\n" + "\n".join(f" - {c}" for c in commits))

    bullets = await summarizer.generate_journal_bullets(
        repo_name="resumesh-llm", commits=commits
    )

    print("\n--- Polished Impact Bullet Points ---")
    for idx, bullet in enumerate(bullets, 1):
        print(f"{idx}. {bullet}")


if __name__ == "__main__":
    asyncio.run(main())
