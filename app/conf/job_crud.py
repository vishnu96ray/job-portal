from ..model.job_service import JobPost, Resume
from ..schemas.job import JobCreate
import os
import shutil
from bson import ObjectId
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List, Optional, Dict, Any
from dateutil import parser


ALLOWED_EXTENSIONS = {"pdf"}


async def create_job(job: JobCreate) -> JobPost:
    try:
        new_job = JobPost(
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary,
            job_experience=job.job_experience,
            # Convert enum to string
            status=job.status.value,
            highlights=job.highlights,
            # Convert nested model to dict
            job_description=job.job_description.dict(),  
            more_info=job.more_info.dict(),
            recruiter_information=job.recruiter_information,
            views=0,
            applied=0
        )
        await new_job.insert()
        return new_job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_job(job_id: str):
    try:
        job = await JobPost.get(ObjectId(job_id))
        if job and not job.deleted:
            job.views += 1
            await job.save()
            return job
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_jobs_by_status(status: str) -> List[JobPost]:
    try:
        jobs = await JobPost.find((JobPost.status == status) & (JobPost.deleted == False)).to_list()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_job(job_id: str, job: JobCreate) -> Optional[JobPost]:
    try:
        existing_job = await JobPost.get(ObjectId(job_id))
        if existing_job and not existing_job.deleted:
            job_data = job.dict(exclude_unset=True, exclude_none=True)
            for key, value in job_data.items():
                if key in ["job_description", "more_info"] and value is not None:
                    # Merge nested dictionaries
                    nested_obj = getattr(existing_job, key).dict()
                    nested_obj.update(value)
                    value = nested_obj
                setattr(existing_job, key, value)
            await existing_job.save()
            return existing_job
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_job(job_id: str):
    try:
        job = await JobPost.get(ObjectId(job_id))
        if job:
            await job.delete()
            return True
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_job_not_permanent(job_id: str):
    try:
        job = await JobPost.get(ObjectId(job_id))
        if job:
            job.deleted = True
            await job.save()
            return True
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_job_views(job_id: str):
    try:
        job = await JobPost.get(ObjectId(job_id))
        if job and not job.deleted:
            return job.views
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def apply_for_job(job_id: str) -> bool:
    try:
        job = await JobPost.get(ObjectId(job_id))
        if not job or job.deleted:
            raise HTTPException(status_code=404, detail="Job not found")
        job.applied += 1
        await job.save()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def upload_resume(job_id: str, file):
    try:
        job = await JobPost.get(ObjectId(job_id))
        if not job or job.deleted:
            raise HTTPException(status_code=404, detail="Job not found or job has been deleted")

        if not is_valid_file_extension(file.filename):
            raise HTTPException(status_code=400, detail="Invalid file extension")
        
        file_location = f"resumes/{job_id}/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        resume = Resume(job_id=job_id, filename=file.filename, path=file_location)
        await resume.insert()
        return resume
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def is_valid_file_extension(filename: str) -> bool:
    if '.' in filename:
        # Get file extension and convert to lower case
        extension = filename.rsplit(".", 1)[-1].lower()  
        return extension in ALLOWED_EXTENSIONS
    return False

async def save_file(file: UploadFile, file_location: str):
    async with aiofiles.open(file_location, 'wb') as buffer:
        # Read file in chunks
        while chunk := await file.read(1024):
            await buffer.write(chunk)

async def get_filtered_jobs(filter_params: Dict[str, Any]) -> List[JobPost]:
    try:
        query = {"deleted": False}
        if filter_params.get('title'):
            query['title'] = {"$regex": filter_params['title'], "$options": "i"}
        if filter_params.get('company'):
            query['company'] = {"$regex": filter_params['company'], "$options": "i"}
        if filter_params.get('location'):
            query['location'] = {"$regex": filter_params['location'], "$options": "i"}
        if filter_params.get('job_experience'):
            query['job_experience'] = {"$regex": filter_params['job_experience'], "$options": "i"}
        if filter_params.get('salary'):
            query['salary'] = {"$regex": filter_params['salary'], "$options": "i"}
        if filter_params.get('date_of_jobpost_from') or filter_params.get('date_of_jobpost_to'):
            date_query = {}
            if filter_params.get('date_of_jobpost_from'):
                try:
                    date_query['$gte'] = parser.isoparse(filter_params['date_of_jobpost_from'])
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid date format for 'date_of_jobpost_from'. Please use one of the following formats: "
                            "YYYY-MM-DDTHH:MM:SS.sss, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM, YYYY-MM-DDTHH, or YYYY-MM-DD. and YYYY"
                    )
            if filter_params.get('date_of_jobpost_to'):
                try:
                    date_query['$lte'] = parser.isoparse(filter_params['date_of_jobpost_to'])
                except ValueError:
                    raise HTTPException(
                        status_code = 400,
                        detail="Invalid date format for 'date_of_jobpost_to'. Please use one of the following formats: "
                            "YYYY-MM-DDTHH:MM:SS.sss, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM, YYYY-MM-DDTHH, or YYYY-MM-DD. and YYYY"
                    )
            query['date_of_jobpost'] = date_query
        jobs = await JobPost.find(query).sort(("date_of_jobpost", 1)).to_list()
        return jobs
    except HTTPException as e:
        raise str(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))