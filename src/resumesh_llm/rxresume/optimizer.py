import json

from pydantic import BaseModel, Field

from resumesh_llm.core.client import LLMClient
from resumesh_llm.core.models import LLMRequest
from resumesh_llm.core.prompt_loader import PromptLoader


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


class CVOptimizer:
    """Service providing professional LLM capabilities to optimize, extract, and align CVs/Resumes."""

    def __init__(self, client: LLMClient):
        """Initializes the CVOptimizer with a concrete LLMClient.

        Args:
            client: LLMClient instance.
        """
        self.client = client

    async def optimize_bullet_point(
        self, raw_bullet: str, context: str | None = None
    ) -> BulletPointOptimizationResult:
        """Optimizes a resume work experience bullet point using the Google-pioneered XYZ formula:

        "Accomplished [X] as measured by [Y], by doing [Z]"

        Args:
            raw_bullet: The original unoptimized bullet point.
            context: Optional context (e.g., job role, industry, or company).

        Returns:
            BulletPointOptimizationResult with optimized text and explanation.
        """
        system_instruction = PromptLoader.load_and_render(
            domain="rxresume", template_name="optimize_bullet_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="rxresume",
            template_name="optimize_bullet_user",
            raw_bullet=raw_bullet,
            context=context,
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.4,
            response_format="json_object",
        )

        # Generate response using LLMClient
        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return BulletPointOptimizationResult(
                original=raw_bullet,
                optimized=data.get("optimized", raw_bullet),
                explanation=data.get("explanation", ""),
            )
        except (json.JSONDecodeError, TypeError):
            return BulletPointOptimizationResult(
                original=raw_bullet,
                optimized=f"Enhanced experience: {raw_bullet}",
                explanation="Could not format optimized response properly.",
            )

    async def extract_skills(self, text: str) -> SkillExtractionResult:
        """Extracts and categorizes skills from any CV/Resume text or job description.

        Args:
            text: Raw text to extract skills from.

        Returns:
            SkillExtractionResult containing categorized lists of skills.
        """
        system_instruction = PromptLoader.load_and_render(
            domain="rxresume", template_name="extract_skills_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="rxresume", template_name="extract_skills_user", text=text
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,
            response_format="json_object",
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return SkillExtractionResult(
                hard_skills=data.get("hard_skills", []),
                soft_skills=data.get("soft_skills", []),
                tools_and_platforms=data.get("tools_and_platforms", []),
            )
        except (json.JSONDecodeError, TypeError):
            return SkillExtractionResult()

    async def analyze_alignment(
        self, cv_text: str, job_description: str
    ) -> JobAlignmentResult:
        """Analyzes a candidate's CV text against a Job Description to compute a match score,

        identify missing skills/keywords, and provide tailored improvement recommendations.

        Args:
            cv_text: Raw text of the resume/CV.
            job_description: Raw text of the target job description.

        Returns:
            JobAlignmentResult.
        """
        system_instruction = PromptLoader.load_and_render(
            domain="rxresume", template_name="analyze_alignment_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="rxresume",
            template_name="analyze_alignment_user",
            cv_text=cv_text,
            job_description=job_description,
        )

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            response_format="json_object",
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return JobAlignmentResult(
                match_score=data.get("match_score", 0),
                missing_skills=data.get("missing_skills", []),
                matching_skills=data.get("matching_skills", []),
                suggestions=data.get("suggestions", []),
            )
        except (json.JSONDecodeError, TypeError):
            return JobAlignmentResult(
                match_score=0,
                missing_skills=[],
                matching_skills=[],
                suggestions=["Could not evaluate CV alignment. Please check inputs."],
            )
