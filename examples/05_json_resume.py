from resumesh_llm import JSONResume, JSONResumeBasics, JSONResumeSkill, JSONResumeWork


def main():
    print("--- 05. JSON Resume Standardization Example ---")

    # Construct standard schema
    resume = JSONResume(
        basics=JSONResumeBasics(
            name="Alice Developer",
            label="Backend Architect",
            email="alice@example.com",
            phone="+123456789",
            url="https://alice.dev",
        ),
        work=[
            JSONResumeWork(
                name="CloudScale Corp",
                position="Technical Lead",
                startDate="2024-01-01",
                summary="Lead architect for multi-cloud deployments.",
                highlights=[
                    "Refactored database interfaces into single-responsibility modules.",
                    "Improved API throughput by 35% using asynchronous connection pools.",
                ],
            )
        ],
        skills=[
            JSONResumeSkill(
                name="Programming Languages", keywords=["Python", "Go", "TypeScript"]
            )
        ],
    )

    # Convert to JSON Resume schema dictionary
    resume_dict = resume.model_dump(exclude_unset=True)

    print("\n--- Valid JSON Resume Output ---")
    import json

    print(json.dumps(resume_dict, indent=2))


if __name__ == "__main__":
    main()
