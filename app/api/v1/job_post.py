from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile, Request
from app.model.job_service import Resume
from app.schemas.job import JobCreate, JobOut, ResumeOut
from app.conf import job_crud
import os


router = APIRouter(prefix="/jobs")


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail={"error": detail})

@router.post(
        "",
        tags=["Job"],
        status_code=status.HTTP_201_CREATED,
        summary="Create a Job",
        response_model=JobCreate,
    )
async def create_job_endpoint(job: JobCreate, request: Request):
    try:
        created_job = await job_crud.create_job(job)
        return created_job
    except Exception as e:
        raise CustomHTTPException(status_code=400, detail=str(e))
   

@router.get(
        "",
        tags=["Job"],
        summary="Get Job endpoint",
)
async def get_job_endpoint(request: Request, job_id: str = Query(...)):
    job = await job_crud.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch(
        "",
        tags=["Job"],
        summary="Update Job",
        response_model=JobOut
)
async def update_job_endpoint(
    job: JobCreate,
    job_id: str = Query(...)
    ):
    updated_job = await job_crud.update_job(job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job


@router.delete(
        "",
        tags=["Job"],
        summary="Delete Job",
)
async def delete_job_endpoint(job_id: str = Query(...)):
    if not await job_crud.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"msg": "Job deleted"}


@router.get(
        "/filter",
        tags=["Job"],
        summary="Filter Jobs by Status"
)
async def filter_jobs_by_status(status: str = Query(..., description="Filter jobs by status (active, closed, draft)")):
    jobs = await job_crud.get_jobs_by_status(status)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found with the given status")
    return jobs

@router.post(
        "/upload_resume",
        tags=["Job"],
        status_code=status.HTTP_201_CREATED,
        summary="Upload Remuse",
        response_model=ResumeOut
)
async def upload_resume_endpoint(
    job_id: str = Query(...),
    file: UploadFile = File(...)
    ):
    
    if not job_crud.is_valid_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_location = f"resumes/{job_id}-{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    await job_crud.save_file(file, file_location)
    
    resume = Resume(job_id=job_id, filename=file.filename, path=file_location)
    await resume.insert()
    return ResumeOut(job_id=resume.job_id, filename=resume.filename, path=resume.path)


@router.get(
        "/views",
        tags=["Job"],
        summary="Get Job View"
)
async def get_job_views_endpoint(job_id: str = Query(...)):
    views = await job_crud.get_job_views(job_id)
    if views is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "views": views}

@router.get(
        "/apply",
        tags=["Job"],
        summary="Apply for Job"
)
async def job_apply_endpoint(job_id: str = Query(...)):
    success = await job_crud.apply_for_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"msg": "Successfully applied for the job"}


@router.get(
    "/global/filter",
    tags=["Job"],
    summary="Global Jobs Filter",
    # response_model=List[JobOut],
)
async def global_filter_endpoint(
    title: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_experience: Optional[str] = Query(None),
    salary: Optional[str] = Query(None),
    date_of_jobpost_from: Optional[str] = Query(None, description="Filter jobs posted from this date (YYYY-MM-DD)"),
    date_of_jobpost_to: Optional[str] = Query(None, description="Filter jobs posted to this date (YYYY-MM-DD)")
):
    filter_params = {
        "title": title,
        "company": company,
        "location": location,
        "job_experience": job_experience,
        "salary": salary,
        "date_of_jobpost_from": date_of_jobpost_from,
        "date_of_jobpost_to": date_of_jobpost_to
    
    }
    jobs = await job_crud.get_filtered_jobs(filter_params)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found matching the criteria")
    return jobs