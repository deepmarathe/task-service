# tests/test_main.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"
    assert response.json()["description"] == "Test description"
    assert response.json()["status"] == "pending"
    assert "id" in response.json()

def test_get_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_task():
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Management Service is running"}
