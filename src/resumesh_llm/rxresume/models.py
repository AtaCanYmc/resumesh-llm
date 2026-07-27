from pydantic import BaseModel, Field


class BulletPointOptimizationResult(BaseModel):
    """Result of bullet point optimization."""

    original: str = Field(description="The original input bullet point")
    optimized: str = Field(
        description="The optimized version using the XYZ formula (Accomplished [X], measured by [Y], by doing [Z])"
    )
    explanation: str = Field(description="Explanation of what was changed and why")


class SkillExtractionResult(BaseModel):
    """Extracted skills categorized."""

    hard_skills: list[str] = Field(
        default_factory=list,
        description="Technical/hard skills (e.g. Python, Docker, React)",
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="Soft/methodological skills (e.g. Agile, Leadership, Communication)",
    )
    tools_and_platforms: list[str] = Field(
        default_factory=list,
        description="Tools and cloud platforms (e.g. AWS, Git, Jira)",
    )


class JobAlignmentResult(BaseModel):
    """Result of analyzing CV alignment with a Job Description."""

    match_score: int = Field(description="Match score between 0 and 100")
    missing_skills: list[str] = Field(
        description="Important skills or keywords from the job description that are missing from the CV"
    )
    matching_skills: list[str] = Field(
        description="Skills that successfully match between the CV and job description"
    )
    suggestions: list[str] = Field(
        description="Actionable, clear suggestions on how to improve the CV to align with the job description"
    )
