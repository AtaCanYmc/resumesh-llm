# CV Optimization Guide

`CVOptimizer` is a specialized service that helps developers improve their CV quality, classify skills, and match their resumes against target job descriptions.

## Features

### 1. Bullet Point Optimization (Google XYZ Formula)
Google recommends structuring accomplishments as:
> **Accomplished [X], as measured by [Y], by doing [Z].**

`CVOptimizer.optimize_bullet_point` rewrites raw developer descriptions to fit this standard, emphasizing metrics and tools.

**Example transition**:
* **Before**: "I was responsible for fixing database issues."
* **After**: "Optimized query execution time by 45% [Y] by redesigning database indexes and introducing Redis caching [Z]."

### 2. Skill Classification
Extracts skills from text and places them into categorized compartments:
- **Hard Skills**: Languages, frameworks, DBs, engineering concepts (e.g. `Python`, `REST APIs`).
- **Soft Skills**: Management, agile processes, communication (e.g. `Agile`, `Mentorship`).
- **Tools & Platforms**: Platforms and DevOps tools (e.g. `AWS`, `Docker`, `Git`).

### 3. Job Alignment Matcher
Computes alignment metrics between a CV body and a target Job Description. Returns missing keywords and suggestions to tailor the resume.

---

## API Reference

### Bullet Point Optimizer
- **Method**: `async optimize_bullet_point(raw_bullet: str, context: Optional[str]) -> BulletPointOptimizationResult`
- **Output fields**:
  - `original`: original string.
  - `optimized`: XYZ structured string.
  - `explanation`: rationale behind the changes.

### Skill Extractor
- **Method**: `async extract_skills(text: str) -> SkillExtractionResult`
- **Output fields**: `hard_skills`, `soft_skills`, `tools_and_platforms`.

### Job Alignment Analyzer
- **Method**: `async analyze_alignment(cv_text: str, job_description: str) -> JobAlignmentResult`
- **Output fields**:
  - `match_score`: integer from `0` to `100`.
  - `matching_skills`: skills found in both.
  - `missing_skills`: skills required by job but missing in CV.
  - `suggestions`: actionable improvements.
