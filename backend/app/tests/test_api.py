"""Basic API endpoint tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ShiftPilot"


def test_register_and_login():
    # Register a new business and user
    response = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Test Restaurant",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "test@example.com",
            "user_password": "testpass123",
            "user_full_name": "Test Owner",
        },
    )
    assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
    data = response.json()
    assert "access_token" in data

    # Login with same credentials
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert data["access_token"] == token


def test_get_me():
    # Register and get token
    response = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Me Test",
            "business_timezone": "Asia/Kathmandu", 
            "business_currency": "NPR",
            "user_email": "me@test.com",
            "user_password": "testpass123",
            "user_full_name": "Me User",
        },
    )
    token = response.json()["access_token"]
    
    # Get current user
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
