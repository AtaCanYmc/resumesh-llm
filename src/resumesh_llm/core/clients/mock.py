import json
from typing import Any

from resumesh_llm.core.clients.base import LLMClient
from resumesh_llm.core.models.generation_usage import GenerationUsage
from resumesh_llm.core.models.llm_request import LLMRequest
from resumesh_llm.core.models.llm_response import LLMResponse


class MockClient(LLMClient):
    """Mock LLM client useful for development, CI/CD, and fast local prototyping."""

    def __init__(
        self, model_name: str = "mock-model", mock_response: str | None = None
    ):
        super().__init__(model_name)
        self.mock_response = mock_response

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Determine the response text.
        if self.mock_response is not None:
            text_response = self.mock_response
        else:
            if request.response_format == "json_object":
                text_response = json.dumps(
                    {
                        "summary": f"This is a mocked JSON summary response generated for prompt: {request.prompt[:30]}...",
                        "tags": ["mock", "test", "resumesh"],
                        "languages": ["Python", "TypeScript"],
                        "highlights": [
                            "Implemented mock provider client",
                            "Configured robust tests",
                        ],
                        "improvements": [
                            "Enhanced unit testing metrics",
                            "Refactored codebase to SOLID principles",
                        ],
                        "skills": ["Python", "FastAPI", "Docker"],
                        "score": 85,
                        "original": "Wrote some unit tests",
                        "optimized": "Designed and executed a robust test suite, achieving 95% branch coverage.",
                        "explanation": "Added actionable metrics and impact to emphasize software quality.",
                        "hard_skills": ["Python", "FastAPI", "PostgreSQL"],
                        "soft_skills": ["Leadership", "Agile Execution"],
                        "tools_and_platforms": ["Docker", "AWS", "Git"],
                        "match_score": 85,
                        "matching_skills": ["Python", "FastAPI"],
                        "missing_skills": ["Kubernetes", "GraphQL"],
                        "suggestions": [
                            "Add more direct impact metrics to your experience bullets."
                        ],
                    }
                )
            else:
                text_response = f"Mocked response for prompt: {request.prompt[:100]}"

        return LLMResponse(
            text=text_response,
            usage=GenerationUsage(
                prompt_tokens=10, completion_tokens=15, total_tokens=25
            ),
            provider="mock",
            model=self.model_name,
            raw_response={"status": "success", "mocked": True},
        )

    async def generate_structured_output(
        self, request: LLMRequest, response_model: type
    ) -> Any:
        if response_model.__name__ == "ResumeImportData":
            try:
                from reactive_resume.models.resume import Basics, Section, WorkItem

                return response_model(
                    title="Mocked CV",
                    basics=Basics(
                        name="Mock Candidate",
                        headline="Python Developer",
                        email="mock@example.com",
                        phone="123-456-7890",
                        location="Remote",
                    ),
                    sections={
                        "work": Section(
                            id="work",
                            name="Work Experience",
                            items=[
                                WorkItem(
                                    id="mock-w1",
                                    company="Mock Corp",
                                    position="Mock Engineer",
                                    summary="Tailored experience in Python and FastAPI.",
                                )
                            ],
                        )
                    },
                )
            except ImportError:
                pass

        if response_model.__name__ == "LinkedInProfileDataSchema":
            try:
                from app.schemas.certificate import CertificateCreate
                from app.schemas.experience import ExperienceCreate

                return response_model(
                    experiences=[
                        ExperienceCreate(
                            title="Mock Engineer",
                            company_name="Mock Corp",
                            description="Mock experience.",
                            start_date="2020-01-01",
                        )
                    ],
                    certificates=[
                        CertificateCreate(
                            name="Mock Certificate",
                            issuing_organization="Mock Org",
                        )
                    ],
                )
            except ImportError:
                pass

        request.response_format = "json_object"
        res = await self.generate(request)
        try:
            return response_model.model_validate_json(res.text)
        except Exception:
            return response_model.model_construct()
