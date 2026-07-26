import json

from pydantic import BaseModel, Field

from resumesh_llm.core.client import LLMClient
from resumesh_llm.core.models import LLMRequest


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

        system_instruction = (
            "You are a professional technical writer and resume coach. "
            "Your task is to analyze a developer's GitHub repository and summarize it professionally for their portfolio/resume."
        )

        prompt = f"""
Analyze the following raw GitHub repository details:
Repository Name: {repo.repo_name}
Original Description: {repo.description or "None provided"}
Primary Languages (GitHub detected): {', '.join(repo.languages)}
Stats: {repo.stars} stars, {repo.forks} forks

README.md Snippet:
---
{truncated_readme}
---

Generate a professional, structured JSON object with the following fields:
1. "summary": A concise (2-3 sentences), professional, impact-driven description of what the project is, what problem it solves, and the key technology stack used. Focus on value and architectural clarity. Avoid generic phrases like "This repository is...".
2. "tags": A clean list of 4-6 technical tags/topics representing the domain, concepts, or tools (e.g. ["OAuth2", "CI/CD", "Websockets", "Microservices"]).
3. "languages": Refined list of the actual core languages and prominent frameworks/libraries used (e.g. ["Python", "FastAPI", "React", "TypeScript"]).
4. "highlights": A list of 2-3 professional, bullet-point highlights of the technical accomplishments, features, or architectural decisions in the project (e.g. "Designed a high-throughput queue using Redis", "Built responsive UI utilizing CSS variables").

Your response must be a single, valid JSON object matching this schema:
{{
    "summary": "string",
    "tags": ["string"],
    "languages": ["string"],
    "highlights": ["string"]
}}
"""

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
