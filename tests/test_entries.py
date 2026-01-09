import pytest
from fastapi.testclient import TestClient
import mongomock
from bson import ObjectId
from app.main import app
from app import configurations

#project dictionary
example_project = {
    "name": "Test Project",
    "description": "A test project for mongomock",
    "owner_id": "691c8bf8d691e46d00068bf3"
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
    
    #list all the entries for the user
    user_id = "691c8bf8d691e46d00068bf3"
    list_response = client.get(f"/entries/{user_id}")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

def test_delete_entry(client):
    #create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    #delete entry
    delete_response = client.delete(f"/entry/{entry_id}")
    assert delete_response.status_code == 200

def test_update_entry(client):
    #create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    #update entry
    update_data = {"name": "Updated Entry"}
    update_response = client.patch(f"/entries/update/{entry_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Entry"

def test_list_entries_by_project(client):
    #create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    client.put("/entries/", json=entry_data)
    
    #list entries by project
    list_response = client.get(f"/entries/project/{project_id}")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

def test_get_nonexistent_entry(client):
    #try to get entry that doesn't exist
    fake_id = "507f1f77bcf86cd799439011"
    get_response = client.get(f"/entry/{fake_id}")
    assert get_response.status_code == 404

def test_end_already_ended_entry(client):
    #create project and entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    #end entry first time
    client.patch(f"/entries/{entry_id}")
    
    #end again
    patch_response = client.patch(f"/entries/{entry_id}")
    assert patch_response.status_code == 400

def test_list_entries_nonexistent_project(client):
    #list for project that doesn't exist
    fake_project_id = "5675hgytddddffff99439012"
    list_response = client.get(f"/entries/project/{fake_project_id}")
    assert list_response.status_code == 400

def test_get_entry_invalid_id(client):
    # invalid id format
    invalid_id = "invalid_id"
    response = client.get(f"/entry/{invalid_id}")
    assert response.status_code == 400

def test_update_entry_nonexistent(client):
    #update non existant entry
    fake_id = "507f1f77bcf86cd799439011"
    update_data = {"name": "Updated"}
    response = client.patch(f"/entries/update/{fake_id}", json=update_data)
    assert response.status_code == 404

def test_update_entry_with_nonexistent_project(client):
    # create entry
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    entry_data = {"name": "Test Entry", "project_group_id": project_id}
    entry_response = client.put("/entries/", json=entry_data)
    entry_id = entry_response.json()["id"]
    
    # update with bad project id
    fake_project_id = "5675hgytddddffff99439012"
    update_data = {"project_group_id": fake_project_id}
    response = client.patch(f"/entries/update/{entry_id}", json=update_data)
    assert response.status_code == 422