import json

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
