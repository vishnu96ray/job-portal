# schemas.py
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum
from fastapi import Query


class JobStatus(str, Enum):
    active = "active"
    closed = "closed"
    draft = "draft"

class JobDescription(BaseModel):
    job_description: Optional[str] = None
    company_information: Optional[str] = None
    what_company_does: Optional[str] = None
    what_you_need_to_bring: Optional[str] = None
    additional_skills: Optional[List[str]] = None
    health_and_wellbeing: Optional[str] = None
    personal_and_professional_development: Optional[str] = None
    diversity_inclusion_and_belonging: Optional[str] = None
    lets_stay_connected: Optional[str] = None
    job: Optional[str] = None
    job_level: Optional[str] = None

class MoreInfo(BaseModel):
    job_type: Optional[str] = None
    functions: Optional[List[str]] = None
    skills: Optional[List[str]] = None

class JobBase(BaseModel):
    title: str
    company: str
    location: List[str]
    job_experience: str
    salary: int
    status: JobStatus
    highlights: List[str]
    job_description: Optional[JobDescription] = None
    more_info: Optional[MoreInfo] = None
    recruiter_information: str

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    views: int
    applied: int

class JobFilter(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_experience: Optional[str] = None
    salary: Optional[int] = None
    date_of_jobpost_from: Optional[str] = Query(None, description="Filter jobs posted from this date (YYYY-MM-DD)"),
    date_of_jobpost_to: Optional[str] = Query(None, description="Filter jobs posted to this date (YYYY-MM-DD)")

class ResumeCreate(BaseModel):
    job_id: str

class ResumeOut(BaseModel):
    job_id: str
    filename: str
    path: str