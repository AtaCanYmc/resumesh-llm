# GitHub Summarization Guide

The `GitHubSummarizer` converts raw repository data into professional developer highlights and descriptions suitable for a developer resume or portfolio website.

## How it Works

The service uses a prompt template that requests a structured JSON response back from the LLM, containing summary paragraphs, languages list, and technical resume highlights.

```mermaid
sequenceDiagram
    participant App as Application
    participant Service as GitHubSummarizer
    participant Client as LLMClient
    participant LLM as LLM Provider

    App->>Service: summarize_repo(GitHubRepoInput)
    Service->>Service: _truncate_readme(readme_content)
    Service->>Client: generate(LLMRequest)
    Client->>LLM: JSON prompt request
    LLM-->>Client: JSON string output
    Client-->>Service: LLMResponse
    Service->>Service: JSON Parsing & Fallback checks
    Service-->>App: GitHubRepoSummary
```

---

## API Reference

### Input Schema (`GitHubRepoInput`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `repo_name` | `str` | :white_check_mark: | Name of the repository. |
| `description` | `str` | :x: | Original description from GitHub. |
| `readme_content` | `str` | :x: | Readme markdown text. |
| `languages` | `List[str]` | :white_check_mark: | List of programming languages. |
| `stars` | `int` | :x: | Count of stars. |
| `forks` | `int` | :x: | Count of forks. |

### Output Schema (`GitHubRepoSummary`)

- `summary` (`str`): A concise description of the project (2-3 sentences), focusing on value and framework configurations.
- `tags` (`List[str]`): Professional topics (e.g. `OAuth2`, `Websockets`, `CI/CD`).
- `languages` (`List[str]`): Refined framework/language list (e.g. `FastAPI`, `React`, `TypeScript`).
- `highlights` (`List[str]`): Bullet points representing developer impact.

---

## Usage Example

```python
import asyncio
from resumesh_llm import LLMClientFactory, GitHubSummarizer, GitHubRepoInput

async def main():
    # Setup client
    client = LLMClientFactory.get_client(provider="mock")
    summarizer = GitHubSummarizer(client=client)

    # Prepare repository details
    repo = GitHubRepoInput(
        repo_name="ResuMesh-Backend",
        description="FastAPI service for cv building",
        readme_content="# ResuMesh Backend\nIntegrated with supabase storage and sentry tracking.",
        languages=["Python", "Dockerfile"],
        stars=150
    )

    # Process details
    result = await summarizer.summarize_repo(repo)
    print("CV Summary:", result.summary)
    print("Highlights:")
    for bullet in result.highlights:
        print(f" - {bullet}")

    # Generate journal bullets from raw scraper commits
    from resumesh_llm import GitHubCommitModel
    from datetime import datetime
    commits = [
        GitHubCommitModel(
            sha="c1b2a3",
            message="feat: added async state graph engine for agents",
            author_name="Alice",
            author_email="alice@example.com",
            date=datetime.now(),
            repo_name="ResuMesh-Backend",
            repo_full_name="owner/ResuMesh-Backend",
            html_url="https://github.com/owner/ResuMesh-Backend/commit/c1b2a3",
        )
    ]
    bullets = await summarizer.generate_journal_bullets("ResuMesh-Backend", commits)
    print("Journal Bullets:", bullets)

asyncio.run(main())
```

---

## Career Journal API Reference

### Input Model (`GitHubCommitModel`)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `sha` | `str` | :white_check_mark: | Commit hash. |
| `message` | `str` | :white_check_mark: | Commit log message. |
| `author_name` | `str` | :white_check_mark: | Author display name. |
| `author_email` | `str` | :white_check_mark: | Author email address. |
| `date` | `datetime` | :white_check_mark: | Timestamp of the commit. |
| `repo_name` | `str` | :white_check_mark: | Name of the repository. |
| `repo_full_name` | `str` | :white_check_mark: | Full name of the repository (owner/name). |
| `html_url` | `str` | :white_check_mark: | Link to commit on GitHub. |

### Method (`generate_journal_bullets`)

Converts commit logs into XYZ-based resume bullet points.
- **Parameters**:
  - `repo_name` (`str`): Repository name.
  - `commits` (`list[GitHubCommitModel] | list[str]`): Scraped commit objects or raw commit message strings.
- **Returns**: `list[str]` (polished, outcome-driven resume bullet points).
