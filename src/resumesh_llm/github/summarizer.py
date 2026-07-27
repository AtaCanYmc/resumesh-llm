import json

from pydantic import BaseModel, Field

from resumesh_llm.core.client import LLMClient
from resumesh_llm.core.models import LLMRequest
from resumesh_llm.core.prompt_loader import PromptLoader


class GitHubRepoInput(BaseModel):
    """Input payload representing a GitHub repository's raw data."""

    repo_name: str = Field(description="Name of the repository")
    description: str | None = Field(
        default=None, description="Original description on GitHub"
    )
    readme_content: str | None = Field(
        default=None, description="Partial or full content of the README.md"
    )
    languages: list[str] = Field(
        default_factory=list, description="Primary programming languages detected"
    )
    stars: int = Field(default=0, description="Number of repository stargazers")
    forks: int = Field(default=0, description="Number of repository forks")


class GitHubRepoSummary(BaseModel):
    """Structured summary output for a GitHub repository."""

    summary: str = Field(
        description="Professional, impact-driven description of the project suitable for a resume"
    )
    tags: list[str] = Field(
        description="Refined and professional tags/topics describing the project"
    )
    languages: list[str] = Field(
        description="Refined list of primary languages and frameworks utilized"
    )
    highlights: list[str] = Field(
        description="Bullet points representing key technical accomplishments or features of the project"
    )


class GitHubSummarizer:
    """Service to generate professional, resume-ready summaries and highlights from raw GitHub repository data."""

    def __init__(self, client: LLMClient):
        """Initializes the summarizer with a concrete LLMClient.

        Args:
            client: LLMClient instance to use for generations.
        """
        self.client = client

    def _truncate_readme(self, readme: str | None, max_chars: int = 4000) -> str:
        """Helper to truncate readme content to prevent context window overflow."""
        if not readme:
            return ""
        if len(readme) <= max_chars:
            return readme
        return readme[:max_chars] + "\n... [Readme truncated due to length] ..."

    async def summarize_repo(self, repo: GitHubRepoInput) -> GitHubRepoSummary:
        """Generates a professional portfolio-ready summary of a GitHub repository using the configured LLM.

        Args:
            repo: GitHubRepoInput details.

        Returns:
            GitHubRepoSummary containing professional summary, highlights, and tags.
        """
        truncated_readme = self._truncate_readme(repo.readme_content)

        system_instruction = PromptLoader.load_and_render(
            domain="github", template_name="summarize_repo_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="github",
            template_name="summarize_repo_user",
            repo_name=repo.repo_name,
            description=repo.description,
            languages=repo.languages,
            stars=repo.stars,
            forks=repo.forks,
            readme_content=truncated_readme,
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,  # Lower temperature for structure consistency
            response_format="json_object",
        )

        response = await self.client.generate(request)

        try:
            # Parse response
            data = json.loads(response.text)
            return GitHubRepoSummary(
                summary=data.get("summary", ""),
                tags=data.get("tags", []),
                languages=data.get("languages", []),
                highlights=data.get("highlights", []),
            )
        except (json.JSONDecodeError, TypeError):
            # Fallback parsing or standard structured schema if LLM returned bad format
            # In production, we provide a robust fallback to prevent application crashes
            return GitHubRepoSummary(
                summary=repo.description
                or f"A repository named {repo.repo_name} built using {', '.join(repo.languages)}.",
                tags=repo.languages,
                languages=repo.languages,
                highlights=[
                    f"Developed the {repo.repo_name} project using {', '.join(repo.languages)}."
                ],
            )

    async def generate_journal_bullets(
        self, repo_name: str, commits: list[str]
    ) -> list[str]:
        """Pulls commit log messages and translates them into polished, outcome-driven resume bullet points using the Google XYZ formula.

        Args:
            repo_name: Name of the repository.
            commits: List of raw commit messages.

        Returns:
            List of polished bullet points.
        """
        if not commits:
            return []

        system_instruction = PromptLoader.load_and_render(
            domain="github", template_name="journal_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="github",
            template_name="journal_user",
            repo_name=repo_name,
            commits=commits,
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.4,
            response_format="json_object",
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return data.get("bullet_points") or data.get("highlights") or []
        except (json.JSONDecodeError, TypeError):
            # Fallback bullet point
            return [
                f"Contributed {len(commits)} updates to the {repo_name} repository, focusing on codebase maintenance and feature development."
            ]
