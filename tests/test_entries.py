import pytest
from fastapi.testclient import TestClient
import mongomock
from bson import ObjectId
from app.main import app
from app import configurations

#project dictionary
example_project = {
    "name": "Test Project",
    "description": "A test project for mongomock"
}

def test_create_entry_with_project(client):
    #create project
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    #create the entry
    entry_data = {
        "name": "test_create_entry_with_project",
        "project_group_id": project_id
    }
    
    entry_response = client.put("/entries/", json=entry_data)
    assert entry_response.status_code == 201
    assert entry_response.json()["name"] == "test_create_entry_with_project"