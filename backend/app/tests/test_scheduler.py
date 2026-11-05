"""Tests for the Google OR-Tools constraint scheduling engine."""
import pytest
from datetime import date, timedelta

from app.services.scheduler import generate_optimized_schedule


class MockSkill:
    def __init__(self, skill_id: int):
        self.skill_id = skill_id


class MockEmployee:
    def __init__(self, id: int, skill_ids: list, max_hours_per_week: float = 40.0, preferred_days: str = None):
        self.id = id
        self.skills = [MockSkill(sid) for sid in skill_ids]
        self.max_hours_per_week = max_hours_per_week
        self.preferred_days = preferred_days


class MockRequirement:
    def __init__(self, req_id: int, location_id: int, day_of_week_val: int, start_time: str, end_time: str, min_staff: int, skill_id=None):
        self.id = req_id
        self.location_id = location_id
        self.day_of_week = day_of_week_val
        self.start_time = start_time
        self.end_time = end_time
        self.min_staff = min_staff
        self.skill_id = skill_id


class MockAvailability:
    def __init__(self, employee_id: int, date_val: date, is_available: bool = True):
        self.employee_id = employee_id
        self.date = date_val
        self.is_available = is_available


class MockLeaveRequest:
    def __init__(self, employee_id: int, start_date: date, end_date: date, status: str = "approved"):
        self.employee_id = employee_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = type('Status', (), {'value': status})()


def test_scheduler_feasible():
    employees = [
        MockEmployee(1, [1, 2], max_hours_per_week=40),
        MockEmployee(2, [1, 2], max_hours_per_week=40),
    ]
    requirements = [
        MockRequirement(1, 1, 0, "09:00", "17:00", 2, 1),
    ]
    
    start_date = date(2025, 1, 6)  # Monday
    end_date = date(2025, 1, 6)
    
    feasible, shifts, explanations, conflicts = generate_optimized_schedule(
        employees=employees,
        requirements=requirements,
        availabilities=[],
        leave_requests=[],
        start_date=start_date,
        end_date=end_date,
    )
    
    assert feasible == True
    assert len(shifts) == 2


def test_scheduler_with_weights():
    """Test that preference constraints are respected."""
    # Employee 1 prefers Monday (0)
    employees = [
        MockEmployee(1, [1], preferred_days="0"),
        MockEmployee(2, [1], preferred_days="1"),
    ]
    requirements = [
        MockRequirement(1, 1, 0, "09:00", "17:00", 1, 1), # Monday
        MockRequirement(2, 1, 1, "09:00", "17:00", 1, 1), # Tuesday
    ]
    
    start_date = date(2025, 1, 6) # Monday
    end_date = date(2025, 1, 7)   # Tuesday
    
    feasible, shifts, explanations, conflicts = generate_optimized_schedule(
        employees=employees,
        requirements=requirements,
        availabilities=[],
        leave_requests=[],
        start_date=start_date,
        end_date=end_date,
    )
    
    assert feasible == True
    # Emp 1 should work Mon, Emp 2 should work Tue
    for shift in shifts:
        if shift["date"].weekday() == 0:
            assert shift["employee_id"] == 1
        else:
            assert shift["employee_id"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
