import asyncio
import os

from resumesh_llm import (
    CVOptimizer,
    JSONResume,
    JSONResumeBasics,
    JSONResumeSkill,
    JSONResumeWork,
    LLMClientFactory,
)


async def main():
    print("--- 06. Dynamic Gap Analysis (JSON Resume Alignment) Example ---")

    provider = os.getenv("LLM_PROVIDER", "mock")
    client = LLMClientFactory.get_client(
        provider=provider, api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )
    optimizer = CVOptimizer(client=client)

    # Vite/React frontend style structured JSON Resume
    cv_data = JSONResume(
        basics=JSONResumeBasics(
            name="Alice Developer",
            label="Senior Frontend Engineer",
            summary="Experienced React and Vite developer building highly performant web applications.",
        ),
        skills=[
            JSONResumeSkill(
                name="Frontend Web Development",
                level="Senior",
                keywords=["React", "Vite", "TypeScript", "HTML5", "CSS3"],
            ),
            JSONResumeSkill(
                name="Backend & Tooling",
                level="Intermediate",
                keywords=["Node.js", "Git", "Webpack"],
            ),
        ],
        work=[
            JSONResumeWork(
                name="SaaS Solutions Inc.",
                position="Senior Frontend Developer",
                summary="Lead frontend architecture and developer experience migration to Vite.",
                highlights=[
                    "Migrated legacy Webpack project to Vite, reducing dev server startup time by 80%",
                    "Built reusable React component library with Tailwind CSS",
                ],
            )
        ],
    )

    job_description = """
    We are looking for a Senior Frontend Engineer who has deep experience with Vite, React, and TypeScript.
    You will lead our migration projects and improve developer experience.
    Required skills: React, Vite, TypeScript, Tailwind CSS, Kubernetes.
    """

    print("Target Job Description Snippet:")
    print("--------------------------------")
    print(job_description.strip())
    print("--------------------------------\n")

    print("Analyzing Alignment / Dynamic Gap Analysis...")
    result = await optimizer.analyze_alignment(
        cv_text=cv_data, job_description=job_description
    )

    print("\n--- Gamified Alignment Score & Gap Analysis ---")
    print(f"Alignment Score: {result.match_score} / 100")
    print(f"Matching Skills: {', '.join(result.matching_skills)}")
    print(f"Missing Skills: {', '.join(result.missing_skills)}")
    print("\nActionable Improvement Suggestions:")
    for idx, suggestion in enumerate(result.suggestions, 1):
        print(f"{idx}. {suggestion}")


if __name__ == "__main__":
    asyncio.run(main())
