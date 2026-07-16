import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running securely"}

def test_get_users(client: TestClient, mocker, mock_users):
    mocker.patch("api.routes.crud.get_all_users", return_value=mock_users)
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["users"]) == 3
    assert data["users"][0]["name"] == "Isha"

def test_get_current_user_no_header(client: TestClient):
    response = client.get("/api/users/me")
    assert response.status_code == 422
    assert "detail" in response.json()

def test_get_current_user_success(client: TestClient, mocker, mock_users):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.get_user_id", return_value="user1")
    mocker.patch("api.routes.crud.get_all_users", return_value=mock_users)
    
    response = client.get("/api/users/me", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["user"]["name"] == "Isha"

def test_get_current_user_not_found(client: TestClient, mocker, mock_users):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.get_user_id", return_value="unknown_user")
    mocker.patch("api.routes.crud.get_all_users", return_value=mock_users)
    
    response = client.get("/api/users/me", headers={"user-email": "ghost@example.com"})
    assert response.status_code == 404
