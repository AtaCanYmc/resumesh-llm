import json
from typing import Any

from resumesh_llm.core.clients import LLMClient
from resumesh_llm.core.models import LLMRequest
from resumesh_llm.core.prompt_loader import PromptLoader
from resumesh_llm.rxresume.models import (
    BulletPointOptimizationResult,
    JobAlignmentResult,
    SkillExtractionResult,
)
from resumesh_llm.rxresume.utils import format_cv_to_text


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
        self, cv_text: str | dict | Any, job_description: str
    ) -> JobAlignmentResult:
        """Analyzes a candidate's CV text or structured CV object against a Job Description to compute a match score,

        identify missing skills/keywords, and provide tailored improvement recommendations.

        Args:
            cv_text: Raw text of the resume/CV, or JSONResume / dict representation of the resume.
            job_description: Raw text of the target job description.

        Returns:
            JobAlignmentResult.
        """
        formatted_cv = format_cv_to_text(cv_text)

        system_instruction = PromptLoader.load_and_render(
            domain="rxresume", template_name="analyze_alignment_system"
        )

        prompt = PromptLoader.load_and_render(
            domain="rxresume",
            template_name="analyze_alignment_user",
            cv_text=formatted_cv,
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

    async def generate_tailored_cv(
        self, job_description: str, user_context: str, response_model: type
    ) -> Any:
        """Generates a tailored resume matching a job description based on candidate profile context.

        Args:
            job_description: Cleaned job description text.
            user_context: Context about user's skills, projects, experience, certificates, etc.
            response_model: Pydantic model (ResumeImportData) to parse structured output into.

        Returns:
            An instance of response_model containing the tailored CV data.
        """
        prompt = PromptLoader.load_and_render(
            domain="rxresume",
            template_name="generate_cv",
            job_description=job_description,
            user_context=user_context,
        )

        request = LLMRequest(
            prompt=prompt,
            temperature=0.3,
        )

        return await self.client.generate_structured_output(request, response_model)

    async def parse_linkedin_pdf_text(self, raw_text: str, response_model: type) -> Any:
        """Parses raw text extracted from a LinkedIn profile PDF into structured schema data.

        Args:
            raw_text: Text extracted from LinkedIn PDF.
            response_model: Pydantic model (LinkedInProfileDataSchema) to parse into.

        Returns:
            An instance of response_model.
        """
        prompt = PromptLoader.load_and_render(
            domain="rxresume",
            template_name="linkedin_pdf_parser",
            raw_text=raw_text,
        )

        request = LLMRequest(
            prompt=prompt,
            temperature=0.3,
        )

        return await self.client.generate_structured_output(request, response_model)
