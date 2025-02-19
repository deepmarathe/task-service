# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app
import pytest

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
    # Create a task first
    client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) > 0

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

def test_update_task():
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    task_id = create_response.json()["id"]
    
    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated task",
            "description": "Updated description",
            "status": "completed"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["status"] == "completed"

def test_delete_task():
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Test task", "description": "Test description"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify task is deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
