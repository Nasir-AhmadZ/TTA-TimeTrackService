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

#test create entry without project
def test_create_entry_without_project(client):
    entry_data = {
        "name": "test_create_entry_without_project"
    }

    entry_response = client.put("/entries/", json=entry_data)
    assert entry_response.status_code == 422

#test create entry with invalid id
def test_entry_with_invalid_project_id(client):
    entry_data = {
        "name": "test_create_entry_without_project",
        "project_group_id": "8888jjjjj9c5c5ba4bd6e88b"
    }

    entry_response = client.put("/entries/", json=entry_data)
    assert entry_response.status_code == 422

def test_get_entry_by_id(client):
    #create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    # get entry by id
    get_response = client.get(f"/entry/{entry_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Entry"

def test_end_entry(client):
    #create project  and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    #end the entry
    patch_response = client.patch(f"/entries/{entry_id}")
    assert patch_response.status_code == 200
    assert patch_response.json()["endtime"] is not None

def test_list_entries(client):
    # create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    client.put("/entries/", json=entry_data)
    
    #list all the entries
    list_response = client.get("/entries/")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1