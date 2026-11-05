"""Multi-tenant isolation tests."""
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


def test_tenant_isolation():
    """Verify that separate businesses cannot access each other's resources."""
    # Register Business A
    res_a = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Cafe Alpha",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@alpha.com",
            "user_password": "password123",
            "user_full_name": "Alpha Owner",
        },
    )
    assert res_a.status_code == 201
    token_a = res_a.json()["access_token"]

    # Register Business B
    res_b = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Cafe Beta",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@beta.com",
            "user_password": "password123",
            "user_full_name": "Beta Owner",
        },
    )
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]

    # Alpha owner adds an employee
    res_emp = client.post(
        "/api/v1/employees/",
        json={
            "full_name": "Alpha Employee",
            "employment_type": "full_time",
            "contractual_hours_per_week": 40,
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_emp.status_code == 201

    # Beta owner lists employees -> should only see Beta's employees (none yet)
    res_list_b = client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_list_b.status_code == 200
    beta_employees = res_list_b.json()
    assert len(beta_employees) == 0

    # Alpha owner lists employees -> should see Alpha's employee
    res_list_a = client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_list_a.status_code == 200
    alpha_employees = res_list_a.json()
    assert len(alpha_employees) == 1
    assert alpha_employees[0]["full_name"] == "Alpha Employee"


def test_skill_creation_isolation():
    """Verify that skills created by one business are not visible to another."""
    # Register Business A
    res_a = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Restaurant A",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@a.com",
            "user_password": "password123",
            "user_full_name": "Owner A",
        },
    )
    assert res_a.status_code == 201
    token_a = res_a.json()["access_token"]

    # Register Business B
    res_b = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Restaurant B",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@b.com",
            "user_password": "password123",
            "user_full_name": "Owner B",
        },
    )
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]

    # Business A creates a skill
    res_skill_a = client.post(
        "/api/v1/employees/skills",
        json={"name": "Cooking"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_skill_a.status_code == 201

    # Business B tries to list skills -> should only see their own
    res_skills_b = client.get(
        "/api/v1/employees/skills",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_skills_b.status_code == 200
    skills_b = res_skills_b.json()
    assert len(skills_b) == 0

    # Business A lists skills -> should see their own
    res_skills_a = client.get(
        "/api/v1/employees/skills",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_skills_a.status_code == 200
    skills_a = res_skills_a.json()
    assert len(skills_a) == 1
    assert skills_a[0]["name"] == "Cooking"


def test_location_isolation():
    """Verify that locations created by one business are not visible to another."""
    # Register Business A
    res_a = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Store A",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@a.com",
            "user_password": "password123",
            "user_full_name": "Owner A",
        },
    )
    assert res_a.status_code == 201
    token_a = res_a.json()["access_token"]

    # Register Business B
    res_b = client.post(
        "/api/v1/auth/register",
        params={
            "business_name": "Store B",
            "business_timezone": "Asia/Kathmandu",
            "business_currency": "NPR",
            "user_email": "owner@b.com",
            "user_password": "password123",
            "user_full_name": "Owner B",
        },
    )
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]

    # Business A creates a location
    res_loc_a = client.post(
        "/api/v1/auth/locations",
        json={"name": "Main Store"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_loc_a.status_code == 201

    # Business B lists locations -> should only see their own
    res_locs_b = client.get(
        "/api/v1/auth/locations",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_locs_b.status_code == 200
    locations_b = res_locs_b.json()
    assert len(locations_b) == 1
    assert locations_b[0]["name"] == "Main Location"

    # Business A lists locations -> should see their own
    res_locs_a = client.get(
        "/api/v1/auth/locations",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_locs_a.status_code == 200
    locations_a = res_locs_a.json()
    assert len(locations_a) == 2
    assert any(loc["name"] == "Main Store" for loc in locations_a)
