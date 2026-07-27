from typing import Any


def _format_basics(basics: dict) -> list[str]:
    """Formats basics section of CV."""
    lines = []
    name = basics.get("name")
    label = basics.get("label")
    summary = basics.get("summary")
    if name:
        lines.append(f"Name: {name}")
    if label:
        lines.append(f"Headline/Label: {label}")
    if summary:
        lines.append(f"Professional Summary:\n{summary}")
    return lines


def _format_skills(skills: list) -> list[str]:
    """Formats skills section of CV."""
    lines = ["\nSkills:"]
    for s in skills:
        if not isinstance(s, dict):
            continue
        name = s.get("name")
        level = s.get("level")
        keywords = s.get("keywords") or []
        kw_str = f" ({', '.join(keywords)})" if keywords else ""
        lvl_str = f" [{level}]" if level else ""
        if name:
            lines.append(f"- {name}{lvl_str}{kw_str}")
    return lines


def _format_work(work: list) -> list[str]:
    """Formats work section of CV."""
    lines = ["\nWork Experience:"]
    for w in work:
        if not isinstance(w, dict):
            continue
        company = w.get("name") or w.get("company")
        position = w.get("position")
        summary = w.get("summary")
        highlights = w.get("highlights") or []

        job_title = (
            f"{position} at {company}"
            if (position and company)
            else (position or company or "Experience")
        )
        lines.append(f"\n* {job_title}")
        if summary:
            lines.append(f"  Summary: {summary}")
        if highlights:
            lines.append("  Key Accomplishments:")
            for h in highlights:
                lines.append(f"    - {h}")
    return lines


def _format_projects(projects: list) -> list[str]:
    """Formats projects section of CV."""
    lines = ["\nProjects:"]
    for p in projects:
        if not isinstance(p, dict):
            continue
        name = p.get("name")
        desc = p.get("description") or p.get("summary")
        highlights = p.get("highlights") or []
        keywords = p.get("keywords") or []

        lines.append(f"\n* Project: {name}")
        if desc:
            lines.append(f"  Description: {desc}")
        if keywords:
            lines.append(f"  Technologies: {', '.join(keywords)}")
        if highlights:
            lines.append("  Highlights:")
            for h in highlights:
                lines.append(f"    - {h}")
    return lines


def _format_education(education: list) -> list[str]:
    """Formats education section of CV."""
    lines = ["\nEducation:"]
    for ed in education:
        if not isinstance(ed, dict):
            continue
        institution = ed.get("institution")
        area = ed.get("area")
        study_type = ed.get("studyType")
        if institution:
            degree = (
                f"{study_type} in {area}"
                if (study_type and area)
                else (study_type or area or "Degree")
            )
            lines.append(f"- {degree} from {institution}")
    return lines


def format_cv_to_text(cv: str | dict | Any) -> str:
    """Helper to convert various CV inputs (str, dict, JSONResume) into a clean, markdown-friendly text representation for LLM alignment checks."""
    if isinstance(cv, str):
        return cv

    # If it's a dict or a Pydantic model (including JSONResume), extract fields
    data = cv
    if hasattr(cv, "model_dump"):
        data = cv.model_dump()
    elif hasattr(cv, "dict"):
        data = cv.dict()

    if not isinstance(data, dict):
        return str(cv)

    lines = []

    # Basics
    basics = data.get("basics")
    if isinstance(basics, dict) and basics:
        lines.extend(_format_basics(basics))

    # Skills
    skills = data.get("skills")
    if isinstance(skills, list) and skills:
        lines.extend(_format_skills(skills))

    # Work
    work = data.get("work")
    if isinstance(work, list) and work:
        lines.extend(_format_work(work))

    # Projects
    projects = data.get("projects")
    if isinstance(projects, list) and projects:
        lines.extend(_format_projects(projects))

    # Education
    education = data.get("education")
    if isinstance(education, list) and education:
        lines.extend(_format_education(education))

    return "\n".join(lines)
