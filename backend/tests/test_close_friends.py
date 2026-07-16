import pytest
from fastapi.testclient import TestClient

def test_get_close_friends(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.get_close_friends_list", return_value={"success": True, "member_ids": ["user2", "user3"]})
    
    response = client.get("/api/close-friends", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert len(response.json()["member_ids"]) == 2
    assert "user2" in response.json()["member_ids"]

def test_add_close_friend(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.add_close_friend", return_value={"success": True, "data": []})
    
    response = client.post(
        "/api/close-friends", 
        headers={"user-email": "isha@example.com"},
        json={"member_id": "user2"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_add_close_friend_validation_error(client: TestClient):
    response = client.post(
        "/api/close-friends", 
        headers={"user-email": "isha@example.com"},
        json={} # Missing member_id
    )
    assert response.status_code == 422

def test_batch_update_friends(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.batch_update_close_friends", return_value={"success": True, "added": ["user3"], "removed": ["user2"]})
    
    response = client.put(
        "/api/close-friends/batch", 
        headers={"user-email": "isha@example.com"},
        json={"member_ids": ["user3"]}
    )
    assert response.status_code == 200
    assert "user3" in response.json()["added"]
    assert "user2" in response.json()["removed"]

def test_remove_friend(client: TestClient, mocker):
    mocker.patch("api.routes.crud.login_as", return_value=None)
    mocker.patch("api.routes.crud.remove_close_friend", return_value={"success": True})
    
    response = client.delete("/api/close-friends/user2", headers={"user-email": "isha@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True
