import pytest
from fastapi.testclient import TestClient
import io

def test_get_feed_success(client: TestClient, mocker):
    mock_stories = {"success": True, "stories": [{"id": "s1", "owner_name": "Isha"}]}
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.get_visible_stories", return_value=mock_stories)
    
    response = client.get("/api/stories/feed", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert response.json()["stories"][0]["owner_name"] == "Isha"

def test_get_feed_auth_failure(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", side_effect=Exception("Auth error"))
    response = client.get("/api/stories/feed", headers={"user-email": "bad@example.com"})
    assert response.status_code == 401

def test_create_story_missing_file(client: TestClient):
    response = client.post("/api/stories", headers={"user-email": "isha@example.com"})
    assert response.status_code == 422

def test_create_story_success(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.create_story_with_file", return_value={"success": True, "data": []})
    
    file_content = b"fake image content"
    files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}
    response = client.post("/api/stories", headers={"user-email": "isha@example.com"}, files=files)
    
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_create_story_crud_failure(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.create_story_with_file", return_value={"success": False, "error": "Storage full"})
    
    file_content = b"fake image content"
    files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}
    response = client.post("/api/stories", headers={"user-email": "isha@example.com"}, files=files)
    
    assert response.status_code == 400
    assert "Storage full" in response.json()["detail"]

def test_get_story_secure_url(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.download_story_image", return_value={"success": True, "image_url": "https://signed.url"})
    
    response = client.get("/api/stories/user2", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert response.json()["image_url"] == "https://signed.url"

def test_delete_story_success(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.delete_story", return_value={"success": True})
    
    response = client.delete("/api/stories", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
