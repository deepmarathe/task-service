# app/main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# Initialize FastAPI
app = FastAPI(title="Task Management Service")

# Initialize Prometheus metrics
REQUESTS = Counter(
    'task_service_requests_total',
    'Total number of requests by method and endpoint',
    ['method', 'endpoint']
)

LATENCY = Histogram(
    'task_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

TASKS_CREATED = Counter(
    'task_service_tasks_created_total',
    'Total number of tasks created'
)

TASKS_COMPLETED = Counter(
    'task_service_tasks_completed_total',
    'Total number of tasks marked as completed'
)

# Data model
class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "pending"
    created_at: Optional[datetime] = None

# In-memory storage
tasks_db = []
task_counter = 1

# Middleware to track metrics
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    # Record request count
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    
    # Record request duration
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    LATENCY.labels(method=request.method, endpoint=request.url.path).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "Task Management Service is running"}

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    global task_counter
    task.id = task_counter
    task.created_at = datetime.now()
    tasks_db.append(task)
    task_counter += 1
    TASKS_CREATED.inc()  # Increment tasks created counter
    return task

@app.get("/tasks/", response_model=List[Task])
async def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    task = next((task for task in tasks_db if task.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task):
    task_idx = next((idx for idx, task in enumerate(tasks_db) if task.id == task_id), None)
    if task_idx is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    current_task = tasks_db[task_idx]
    update_data = updated_task.dict(exclude_unset=True)
    update_data.pop("id", None)
    update_data.pop("created_at", None)
    
    # Check if task is being marked as completed
    if updated_task.status == "completed" and current_task.status != "completed":
        TASKS_COMPLETED.inc()  # Increment completed counter
    
    updated_task_model = Task(**{**current_task.dict(), **update_data})
    tasks_db[task_idx] = updated_task_model
    return updated_task_model

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    task_idx = next((idx for idx, task in enumerate(tasks_db) if task.id == task_id), None)
    if task_idx is None:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db.pop(task_idx)
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
