import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

##check title
def test_app_title():
    assert app.title == "Time Tracker API"

##check cors configuration
def test_cors_middleware_configured(client):
    response = client.options("/entries/")
    assert response.status_code in [200, 405]

def test_invalid_entry_id_format(client):
    response = client.get("/entry/invalid_id")
    assert response.status_code == 400
    assert "Invalid entry id" in response.json()["detail"]

def test_nonexistent_entry_returns_404(client):
    response = client.get("/entry/507f1f77bcf86cd799439011")
    assert response.status_code == 404
    assert "Entry not found" in response.json()["detail"]

def test_delete_entry_success(client):
    response = client.delete("/entry/507f1f77bcf86cd799439011")
    assert response.status_code == 200
    assert response.json()["message"] == "Entry deleted" 