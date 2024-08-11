# api_route.py

from fastapi import APIRouter, Depends
from typing import List
from model import *
from repository import *
from auth import *

router = APIRouter()


@router.get("/jobs", response_model=List[Job], dependencies=[Depends(get_current_token)])
async def list_jobs(repo: JobRepository = Depends()):
    return repo.list_jobs()


@router.get("/jobs/{job_id}", response_model=Job, dependencies=[Depends(get_current_token)])
async def get_job(job_id: int, repo: JobRepository = Depends()):
    return repo.get_job(job_id)


@router.post("/jobs", response_model=Job, dependencies=[Depends(get_current_token)])
async def create_job(job: JobCreate, repo: JobRepository = Depends()):
    return repo.create_job(job)


@router.delete("/jobs", dependencies=[Depends(get_current_token)])
async def delete_all_jobs(repo: JobRepository = Depends()):
    return repo.delete_all_jobs()


@router.delete("/jobs/{job_id}", dependencies=[Depends(get_current_token)])
async def delete_job(job_id: int, repo: JobRepository = Depends()):
    return repo.delete_job(job_id)
    
    
@router.post("/jobs/schedule", response_model=Job, dependencies=[Depends(get_current_token)])
async def create_scheduled_job(job_schedule: JobSchedule, repo: JobRepository = Depends()):
    return repo.create_scheduled_job(job_schedule)

