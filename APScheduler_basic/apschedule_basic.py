from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

# Set your desired timezone
local_timezone = timezone('Asia/Kolkata')  # Replace with your actual timezone

def job_function():
    print("Scheduled job executed.")

scheduler = BackgroundScheduler(timezone=local_timezone)

# Schedule a job to run every Monday at 9:00 AM
#trigger = CronTrigger(day_of_week='sun', hour=9, minute=35)
trigger = CronTrigger(minute='*')

scheduler.add_job(job_function, trigger)

scheduler.start()

try:
    while True:
        pass  # Keep the script running
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()


