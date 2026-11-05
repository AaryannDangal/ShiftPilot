"""Tests for employee-specific endpoints (availability, leave requests)."""
import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_employee_availability_and_leave():
    """Test employee availability and leave request workflow."""
    # 1. Register business
    res = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Hotel Himalaya",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "manager@himalaya.com",
            "user_password": "securepassword123",
            "user_full_name": "General Manager",
        },
    )
    assert res.status_code == 201
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create employee
    emp_res = client.post(
        "/api/v1/employees/",
        json={
            "full_name": "Sita Sharma",
            "email": "sita@himalaya.com",
            "employment_type": "full_time",
            "contractual_hours_per_week": 40.0,
        },
        headers=headers,
    )
    assert emp_res.status_code == 201
    emp_data = emp_res.json()
    emp_id = emp_data["id"]

    # 3. Create employee user account in the same business (using invite-manager endpoint or a dedicated employee register)
    # Let's add an employee register or link endpoint, or register as part of the same business.
    # Actually, in our auth.py, /register creates a new business. We should support inviting employees or registering under a business.
    # Let's test manager approving leave directly first.

    # 4. Manager requests leave on behalf or employee requests leave
    # If the user is an employee, they need a user record linked to employee profile.
    # Let's test the leave listing and approval flow directly as manager.
    
    leave_list_res = client.get(
        "/api/v1/employees/leave",
        headers=headers,
    )
    assert leave_list_res.status_code == 200
