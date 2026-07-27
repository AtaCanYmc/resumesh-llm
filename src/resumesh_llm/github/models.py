from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GitHubCommitModel(BaseModel):
    """Pydantic model for commit data fetched by the GitHub commits scraper."""

    sha: str
    message: str
    author_name: str
    author_email: str
    date: datetime
    repo_name: str
    repo_full_name: str
    html_url: str

    model_config = ConfigDict(extra="ignore", populate_by_name=True, strict=True)


class GitHubRepoInput(BaseModel):
    """Input payload representing a GitHub repository's raw data."""

    model_config = ConfigDict(strict=True)

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

    model_config = ConfigDict(strict=True)

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
