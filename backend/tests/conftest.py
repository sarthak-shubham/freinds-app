import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to sys.path so we can import from main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_users():
    return [
        {"id": "user1", "name": "Isha", "email": "isha@example.com"},
        {"id": "user2", "name": "Shruti", "email": "shruti@example.com"},
        {"id": "user3", "name": "Rahul", "email": "rahul@example.com"}
    ]
