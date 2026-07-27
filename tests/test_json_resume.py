from resumesh_llm import JSONResume, JSONResumeBasics, JSONResumeWork


def test_json_resume_schema():
    resume = JSONResume(
        basics=JSONResumeBasics(
            name="John Doe", label="Software Engineer", email="john@example.com"
        ),
        work=[
            JSONResumeWork(
                name="Tech Inc",
                position="Senior Developer",
                highlights=[
                    "Designed microservices.",
                    "Optimized DB query times by 20%.",
                ],
            )
        ],
    )

    assert resume.basics.name == "John Doe"
    assert len(resume.work) == 1
    assert resume.work[0].name == "Tech Inc"
    assert "Optimized DB query times by 20%." in resume.work[0].highlights
