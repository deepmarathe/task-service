# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Task Management Service")

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
