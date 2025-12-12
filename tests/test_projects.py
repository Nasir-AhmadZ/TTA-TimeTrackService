import pytest

example_project = {
    "name": "Test Project",
    "description": "A test project"
}

def test_create_project(client):
    response = client.put("/projects/", json=example_project)

    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"

def test_list_projects(client):
    client.put("/projects/", json=example_project)
    response = client.get("/projects/")

    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_list_user_projects(client):
    client.put("/projects/", json=example_project)
    response = client.get("/projects/user")

    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_delete_project(client):
    project_response = client.put("/projects/", json=example_project)
    project_id = project_response.json()["id"]
    
    response = client.delete(f"/project/{project_id}")
    assert response.status_code == 200


def test_delete_user_projects(client):
    client.put("/projects/", json=example_project)
    response = client.delete("/user/projects")
    assert response.status_code == 200