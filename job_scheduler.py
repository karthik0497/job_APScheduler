import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import threading
import time

# Database connection parameters
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/job_schedule_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def check_for_jobs():
    job_details = []
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT job_id, job_name, job_schedule, job_description, job_type, job_params, last_run, created_at, updated_at
                    FROM jobs;
                """)
                jobs = cur.fetchall()
                
                for job in jobs:
                    job_id, job_name, job_schedule, job_description, job_type, job_params, last_run, created_at, updated_at = job
                    # print(
                    #     f"Job ID       : {job_id}\n"
                    #     f"Job Name     : {job_name}\n"
                    #     f"Job Schedule : {job_schedule}\n"
                    #     f"Description  : {job_description}\n"
                    #     f"Type         : {job_type}\n"
                    #     f"Parameters   : {job_params}\n"
                    #     f"Last Run     : {last_run}\n"
                    #     f"Created At   : {created_at}\n"
                    #     f"Updated At   : {updated_at}\n"
                    #     f"{'-'*40}\n"
                    # )
                    job_details.append((job_id, job_name, job_schedule, job_description, job_type))
    except Exception as e:
        print(f"Error checking for jobs: {e}")
    
    return job_details
import json

def get_time_intervals_with_job_id(job_details):
    time_units = {
        'minute': 1,
        'hour': 60,
        'day': 60 * 24,
        'week': 60 * 24 * 7,
        'month': 60 * 24 * 30,  # Approximate month as 30 days
        'year': 60 * 24 * 365   # Approximate year as 365 days
    }
    
    intervals_with_job_id = []
    
    for job_id, job_name, schedule, job_description, job_type in job_details:
        total_minutes = 0

        # Check if schedule is a string and try to convert it to a dictionary
        if isinstance(schedule, str):
            try:
                schedule = json.loads(schedule)
            except json.JSONDecodeError:
                print(f"Error decoding schedule for job_id {job_id}: {schedule}")
                continue

        for unit, factor in time_units.items():
            if unit in schedule:
                total_minutes += schedule[unit] * factor
        
        intervals_with_job_id.append((job_id, job_name, total_minutes, job_description, job_type))
    
    return intervals_with_job_id


def update_last_run(job_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE jobs
                    SET last_run = %s
                    WHERE job_id = %s;
                """, (datetime.now(), job_id))
                conn.commit()
    except Exception as e:
        print(f"Error updating last_run for job_id {job_id}: {e}")

def job_execution(job_id, job_name, job_description, job_type):
    print(f"Executing Job ID: {job_id} | Job Name: {job_name} | Description: {job_description} | Type: {job_type} | Execution Time: {datetime.now()}")
    update_last_run(job_id)

def schedule_jobs_with_apscheduler(job_intervals, scheduler):
    for job_id, job_name, interval, job_description, job_type in job_intervals:
        if not scheduler.get_job(str(job_id)):
            scheduler.add_job(job_execution, IntervalTrigger(minutes=interval), args=[job_id, job_name, job_description, job_type], id=str(job_id))
            print(f"Scheduled Job ID: {job_id} | Interval (minutes): {interval}")

def monitor_for_new_jobs(scheduler):
    while True:
        new_job_details = check_for_jobs()
        new_intervals_with_id = get_time_intervals_with_job_id(new_job_details)
        schedule_jobs_with_apscheduler(new_intervals_with_id, scheduler)
        time.sleep(60)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Initial job scheduling
details = check_for_jobs()
intervals_with_id = get_time_intervals_with_job_id(details)
schedule_jobs_with_apscheduler(intervals_with_id, scheduler)

# Monitor for new jobs in a daemon thread
monitor_thread = threading.Thread(target=monitor_for_new_jobs, args=(scheduler,))
monitor_thread.daemon = True
monitor_thread.start()

# To keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler shut down.")
