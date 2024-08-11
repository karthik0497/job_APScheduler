# model.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


def sequential_id_generator(start: int = 10000):
    current = start
    while True:
        yield current
        current += 1


id_generator = sequential_id_generator()


# Function to get the next ID
def generate_sequential_id():
    return next(id_generator)


# model.py

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Job(BaseModel):
    job_id: int
    job_name: str
    job_schedule: Dict[str, int]
    job_description: str
    job_type: Optional[str]
    job_params: Optional[Dict[str, Any]]
    last_run: Optional[datetime] = None  # Ensure this field is optional with a default value of None


class JobCreate(BaseModel):
    job_name: str
    job_schedule: Dict[str, int]  # Ensure this is a dictionary
    job_description: str
    job_type: Optional[str]
    job_params: Optional[Dict[str, Any]]

class JobSchedule(BaseModel):
    job_name: str
    job_description: Optional[str]
    job_type: Optional[str]
    job_params: Optional[Dict[str, Any]]
    minute: Optional[int]
    hour: Optional[int]
    day: Optional[int]
    week: Optional[int]
    month: Optional[int]
    year: Optional[int]
