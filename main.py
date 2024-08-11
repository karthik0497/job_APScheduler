# main.py

from fastapi import FastAPI
from api_route import router as job_router


app = FastAPI(
    title="Job Scheduler API",
)

app.include_router(job_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
