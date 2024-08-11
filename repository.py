# repository.py

from typing import List
from model import *
from db_conn import get_db_connection
from fastapi import HTTPException, Depends
import json
import psycopg2
from model import Job, JobCreate, JobSchedule
from datetime import datetime

class JobRepository:
    def __init__(self, conn: psycopg2.extensions.connection = Depends(get_db_connection)):
        self.conn = conn

    def list_jobs(self) -> list[Job]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT job_id, job_name, job_schedule, job_description, job_type, job_params, last_run FROM jobs"
            )
            jobs = cursor.fetchall()

            return [
                Job(**dict(zip(["job_id", "job_name", "job_schedule", "job_description", "job_type", "job_params", "last_run"], job)))
                for job in jobs
            ]

    def get_job(self, job_id: int) -> Job:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT job_id, job_name, job_schedule, job_description, job_type, job_params, last_run FROM jobs WHERE job_id = %s",
                (job_id,))
            job = cursor.fetchone()
            if job is None:
                raise HTTPException(status_code=404, detail="Job not found")

            # Ensure `last_run` is handled properly, using `None` if it's not in the result
            return Job(
                **dict(zip(["job_id", "job_name", "job_schedule", "job_description", "job_type", "job_params", "last_run"], job))
            )


    def create_job(self, job: JobCreate) -> Job:
        job_id = generate_sequential_id()
        with self.conn.cursor() as cursor:
            while True:
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_id = %s", (job_id,))
                if cursor.fetchone()[0] == 0:
                    break
                job_id = generate_sequential_id()
            cursor.execute(
                "INSERT INTO jobs (job_id, job_name, job_schedule, job_description, job_type, job_params) VALUES (%s, %s, %s, %s, %s, %s)",
                (job_id, job.job_name, job.job_schedule, job.job_description, job.job_type, json.dumps(job.job_params))
            )
            self.conn.commit()
            return Job(
                job_id=job_id,
                job_name=job.job_name,
                job_schedule=job.job_schedule,
                job_description=job.job_description,
                job_type=job.job_type,
                job_params=job.job_params
            )

    def delete_all_jobs(self) -> dict:
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM jobs")
            self.conn.commit()
        return {"message": "All jobs have been deleted successfully"}

    def delete_job(self, job_id: int) -> dict:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_id = %s", (job_id,))
            if cursor.fetchone()[0] == 0:
                raise HTTPException(status_code=404, detail="Job not found")
            cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
            self.conn.commit()
        return {"message": f"Job with ID {job_id} has been deleted successfully"}
        
    # repository.py

    def create_scheduled_job(self, job_schedule: JobSchedule) -> Job:
        job_id = generate_sequential_id()
        with self.conn.cursor() as cursor:
            while True:
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_id = %s", (job_id,))
                if cursor.fetchone()[0] == 0:
                    break
                job_id = generate_sequential_id()
            
            schedule_dict = {
                "minute": job_schedule.minute,
                "hour": job_schedule.hour,
                "day": job_schedule.day,
                "week": job_schedule.week,
                "month": job_schedule.month,
                "year": job_schedule.year,
            }
            
            cursor.execute(
                "INSERT INTO jobs (job_id, job_name, job_schedule, job_description, job_type, job_params) VALUES (%s, %s, %s, %s, %s, %s)",
                (job_id, job_schedule.job_name, json.dumps(schedule_dict), job_schedule.job_description, job_schedule.job_type, json.dumps(job_schedule.job_params))
            )
            self.conn.commit()
            
            return Job(
                job_id=job_id,
                job_name=job_schedule.job_name,
                job_schedule=schedule_dict,
                job_description=job_schedule.job_description,
                job_type=job_schedule.job_type,
                job_params=job_schedule.job_params,
                last_run=None  # Set default value for last_run
            )
