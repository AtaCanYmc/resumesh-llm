from typing import Any

from pydantic import BaseModel, Field


class JSONResumeProfile(BaseModel):
    network: str | None = None
    username: str | None = None
    url: str | None = None


class JSONResumeLocation(BaseModel):
    address: str | None = None
    postalCode: str | None = None
    city: str | None = None
    countryCode: str | None = None
    region: str | None = None


class JSONResumeBasics(BaseModel):
    name: str | None = None
    label: str | None = None
    image: str | None = None
    email: str | None = None
    phone: str | None = None
    url: str | None = None
    summary: str | None = None
    location: JSONResumeLocation | None = None
    profiles: list[JSONResumeProfile] = Field(default_factory=list)


class JSONResumeWork(BaseModel):
    name: str | None = None
    position: str | None = None
    url: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    summary: str | None = None
    highlights: list[str] = Field(default_factory=list)


class JSONResumeVolunteer(BaseModel):
    organization: str | None = None
    position: str | None = None
    url: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    summary: str | None = None
    highlights: list[str] = Field(default_factory=list)


class JSONResumeEducation(BaseModel):
    institution: str | None = None
    url: str | None = None
    area: str | None = None
    studyType: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    score: str | None = None
    courses: list[str] = Field(default_factory=list)


class JSONResumeAward(BaseModel):
    title: str | None = None
    date: str | None = None
    awarder: str | None = None
    summary: str | None = None


class JSONResumeCertificate(BaseModel):
    name: str | None = None
    date: str | None = None
    issuer: str | None = None
    url: str | None = None


class JSONResumePublication(BaseModel):
    name: str | None = None
    publisher: str | None = None
    releaseDate: str | None = None
    url: str | None = None
    summary: str | None = None


class JSONResumeSkill(BaseModel):
    name: str | None = None
    level: str | None = None
    keywords: list[str] = Field(default_factory=list)


class JSONResumeLanguage(BaseModel):
    language: str | None = None
    fluency: str | None = None


class JSONResumeInterest(BaseModel):
    name: str | None = None
    keywords: list[str] = Field(default_factory=list)


class JSONResumeReference(BaseModel):
    name: str | None = None
    reference: str | None = None


class JSONResumeProject(BaseModel):
    name: str | None = None
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    startDate: str | None = None
    endDate: str | None = None
    url: str | None = None
    roles: list[str] = Field(default_factory=list)
    entity: str | None = None
    type: str | None = None


class JSONResume(BaseModel):
    """The standard, open-source JSON Resume schema.

    Enables developers to serialize and direct-map resumesh-llm
    optimized content directly into hundreds of JSON Resume visual themes.
    """

    basics: JSONResumeBasics | None = None
    work: list[JSONResumeWork] = Field(default_factory=list)
    volunteer: list[JSONResumeVolunteer] = Field(default_factory=list)
    education: list[JSONResumeEducation] = Field(default_factory=list)
    awards: list[JSONResumeAward] = Field(default_factory=list)
    certificates: list[JSONResumeCertificate] = Field(default_factory=list)
    publications: list[JSONResumePublication] = Field(default_factory=list)
    skills: list[JSONResumeSkill] = Field(default_factory=list)
    languages: list[JSONResumeLanguage] = Field(default_factory=list)
    interests: list[JSONResumeInterest] = Field(default_factory=list)
    references: list[JSONResumeReference] = Field(default_factory=list)
    projects: list[JSONResumeProject] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
