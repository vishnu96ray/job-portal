from datetime import datetime
from typing import List

from beanie import Document
from pydantic import Field, BaseModel

class JobDescription(BaseModel):
    job_description: str
    company_information: str
    what_company_does: str
    what_you_need_to_bring: str
    additional_skills: List[str]
    health_and_wellbeing: str
    personal_and_professional_development: str
    diversity_inclusion_and_belonging: str
    lets_stay_connected: str
    job: str
    job_level: str

class MoreInfo(BaseModel):
    job_type: str
    functions: List[str]
    skills: List[str]

class JobPost(Document):
    title: str
    company: str
    location: List[str]
    job_experience: str
    status: str
    salary: int
    date_of_jobpost: datetime = Field(default_factory=datetime.utcnow)
    highlights: List[str]
    job_description: JobDescription
    more_info: MoreInfo
    recruiter_information: str
    views: int = 0
    applied: int = 0
    deleted: bool = Field(default=False)  # Added deleted flag

    class Settings:
        collection = "jobs"


class Resume(Document):
    job_id: str
    filename: str
    path: str

    class Settings:
        collection = "resumes"
