import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from resumesh_llm.core.client import LLMClient
from resumesh_llm.core.models import LLMRequest


class BulletPointOptimizationResult(BaseModel):
    """Result of bullet point optimization."""
    original: str = Field(description="The original input bullet point")
    optimized: str = Field(description="The optimized version using the XYZ formula (Accomplished [X], measured by [Y], by doing [Z])")
    explanation: str = Field(description="Explanation of what was changed and why")


class SkillExtractionResult(BaseModel):
    """Extracted skills categorized."""
    hard_skills: List[str] = Field(default_factory=list, description="Technical/hard skills (e.g. Python, Docker, React)")
    soft_skills: List[str] = Field(default_factory=list, description="Soft/methodological skills (e.g. Agile, Leadership, Communication)")
    tools_and_platforms: List[str] = Field(default_factory=list, description="Tools and cloud platforms (e.g. AWS, Git, Jira)")


class JobAlignmentResult(BaseModel):
    """Result of analyzing CV alignment with a Job Description."""
    match_score: int = Field(description="Match score between 0 and 100")
    missing_skills: List[str] = Field(description="Important skills or keywords from the job description that are missing from the CV")
    matching_skills: List[str] = Field(description="Skills that successfully match between the CV and job description")
    suggestions: List[str] = Field(description="Actionable, clear suggestions on how to improve the CV to align with the job description")


class CVOptimizer:
    """Service providing professional LLM capabilities to optimize, extract, and align CVs/Resumes."""

    def __init__(self, client: LLMClient):
        """Initializes the CVOptimizer with a concrete LLMClient.

        Args:
            client: LLMClient instance.
        """
        self.client = client

    async def optimize_bullet_point(self, raw_bullet: str, context: Optional[str] = None) -> BulletPointOptimizationResult:
        """Optimizes a resume work experience bullet point using the Google-pioneered XYZ formula:

        "Accomplished [X] as measured by [Y], by doing [Z]"

        Args:
            raw_bullet: The original unoptimized bullet point.
            context: Optional context (e.g., job role, industry, or company).

        Returns:
            BulletPointOptimizationResult with optimized text and explanation.
        """
        system_instruction = (
            "You are a professional resume writer specializing in the tech industry. "
            "Your job is to rewrite raw experience bullets using the XYZ formula: "
            "Accomplished [X] (the outcome) as measured by [Y] (quantifiable metrics/data), by doing [Z] (the actions/skills utilized)."
        )

        prompt = f"""
Optimize the following resume bullet point. If the original lacks metrics or specific details, make realistic/plausible assumptions or provide placeholders like "[metric]%" but prefer general action/outcome structure.

Original Bullet: "{raw_bullet}"
Role/Industry Context: {context or "Not provided"}

Your response must be a single, valid JSON object matching this schema:
{{
    "original": "string",
    "optimized": "string",
    "explanation": "string"
}}
"""

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.4,
            response_format="json_object"
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return BulletPointOptimizationResult(
                original=raw_bullet,
                optimized=data.get("optimized", raw_bullet),
                explanation=data.get("explanation", "")
            )
        except (json.JSONDecodeError, TypeError):
            return BulletPointOptimizationResult(
                original=raw_bullet,
                optimized=f"Enhanced experience: {raw_bullet}",
                explanation="Could not format optimized response properly."
            )

    async def extract_skills(self, text: str) -> SkillExtractionResult:
        """Extracts and categorizes skills from any CV/Resume text or job description.

        Args:
            text: Raw text to extract skills from.

        Returns:
            SkillExtractionResult containing categorized lists of skills.
        """
        system_instruction = (
            "You are an AI recruiter. Your task is to extract and categorize skills from the provided text."
        )

        prompt = f"""
Analyze the following text and extract all professional skills, tools, and platforms mentioned or strongly implied.

Text:
---
{text}
---

Categorize them into:
1. "hard_skills": Languages, frameworks, core software engineering practices, databases, methodologies (e.g., Python, SQL, REST APIs, TDD).
2. "soft_skills": Interpersonal, leadership, or execution attributes (e.g., Team Management, Agile, Public Speaking).
3. "tools_and_platforms": Specific software tools, cloud providers, or platforms (e.g., AWS, Git, Docker, Kubernetes, Jira).

Your response must be a single, valid JSON object matching this schema:
{{
    "hard_skills": ["string"],
    "soft_skills": ["string"],
    "tools_and_platforms": ["string"]
}}
"""

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,
            response_format="json_object"
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return SkillExtractionResult(
                hard_skills=data.get("hard_skills", []),
                soft_skills=data.get("soft_skills", []),
                tools_and_platforms=data.get("tools_and_platforms", [])
            )
        except (json.JSONDecodeError, TypeError):
            return SkillExtractionResult()

    async def analyze_alignment(self, cv_text: str, job_description: str) -> JobAlignmentResult:
        """Analyzes a candidate's CV text against a Job Description to compute a match score,

        identify missing skills/keywords, and provide tailored improvement recommendations.

        Args:
            cv_text: Raw text of the resume/CV.
            job_description: Raw text of the target job description.

        Returns:
            JobAlignmentResult.
        """
        system_instruction = (
            "You are an ATS (Applicant Tracking System) optimizer and career consultant. "
            "Analyze CV alignment against a Job Description to evaluate matches and provide improvements."
        )

        prompt = f"""
Compare the candidate's CV/Resume text against the Job Description.

CV/Resume Content:
---
{cv_text}
---

Job Description:
---
{job_description}
---

Evaluate the alignment and generate a JSON object with:
1. "match_score": An integer between 0 and 100 based on keyword overlap, level of experience match, and technical alignment.
2. "missing_skills": Top skills, libraries, technologies, or keywords required in the job description that are not mentioned in the CV.
3. "matching_skills": Technologies or skills mentioned in both documents.
4. "suggestions": Concise, actionable bullets advising the candidate on how to rewrite or re-highlight sections to better fit the role.

Your response must be a single, valid JSON object matching this schema:
{{
    "match_score": 75,
    "missing_skills": ["string"],
    "matching_skills": ["string"],
    "suggestions": ["string"]
}}
"""

        request = LLMRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            response_format="json_object"
        )

        response = await self.client.generate(request)

        try:
            data = json.loads(response.text)
            return JobAlignmentResult(
                match_score=data.get("match_score", 0),
                missing_skills=data.get("missing_skills", []),
                matching_skills=data.get("matching_skills", []),
                suggestions=data.get("suggestions", [])
            )
        except (json.JSONDecodeError, TypeError):
            return JobAlignmentResult(
                match_score=0,
                missing_skills=[],
                matching_skills=[],
                suggestions=["Could not evaluate CV alignment. Please check inputs."]
            )
