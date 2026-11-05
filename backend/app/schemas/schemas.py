"""Pydantic schemas for API request/response validation."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class BusinessCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    timezone: str = "Asia/Kathmandu"
    currency: str = "NPR"


class BusinessOut(BaseModel):
    id: int
    name: str
    slug: str
    status: str
    timezone: str
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=200)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    address: Optional[str] = None


class LocationOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class SkillOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    employment_type: str = "full_time"
    hourly_wage: float = 0.0
    position: Optional[str] = None
    contractual_hours_per_week: float = 40.0
    max_hours_per_week: float = 48.0
    min_hours_per_week: float = 0.0
    max_consecutive_days: int = 6
    min_rest_hours_between_shifts: float = 11.0
    preferred_days: Optional[str] = None
    unavailable_days: Optional[str] = None
    start_date: Optional[date] = None
    skill_ids: List[int] = []


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    employment_type: Optional[str] = None
    hourly_wage: Optional[float] = None
    position: Optional[str] = None
    contractual_hours_per_week: Optional[float] = None
    max_hours_per_week: Optional[float] = None
    min_hours_per_week: Optional[float] = None
    max_consecutive_days: Optional[int] = None
    min_rest_hours_between_shifts: Optional[float] = None
    preferred_days: Optional[str] = None
    unavailable_days: Optional[str] = None
    is_active: Optional[bool] = None
    skill_ids: Optional[List[int]] = None


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    employment_type: str
    hourly_wage: float
    position: Optional[str]
    contractual_hours_per_week: float
    max_hours_per_week: float
    min_hours_per_week: float
    max_consecutive_days: int
    min_rest_hours_between_shifts: float
    preferred_days: Optional[str]
    unavailable_days: Optional[str]
    start_date: Optional[date]
    is_active: bool
    skills: List[SkillOut] = []

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, employee):
        skills = []
        if hasattr(employee, 'skills'):
            for emp_skill in employee.skills:
                skills.append(SkillOut(
                    id=emp_skill.skill_id,
                    name=emp_skill.skill.name,
                    description=emp_skill.skill.description
                ))
        return cls(
            id=employee.id,
            full_name=employee.full_name,
            email=employee.email,
            phone=employee.phone,
            employment_type=employee.employment_type,
            hourly_wage=employee.hourly_wage,
            position=employee.position,
            contractual_hours_per_week=employee.contractual_hours_per_week,
            max_hours_per_week=employee.max_hours_per_week,
            min_hours_per_week=employee.min_hours_per_week,
            max_consecutive_days=employee.max_consecutive_days,
            min_rest_hours_between_shifts=employee.min_rest_hours_between_shifts,
            preferred_days=employee.preferred_days,
            unavailable_days=employee.unavailable_days,
            start_date=employee.start_date,
            is_active=employee.is_active,
            skills=skills
        )


class AvailabilityCreate(BaseModel):
    employee_id: int
    date: date
    is_available: bool = True
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    note: Optional[str] = None


class AvailabilityOut(BaseModel):
    id: int
    employee_id: int
    date: date
    is_available: bool
    start_time: Optional[str]
    end_time: Optional[str]
    note: Optional[str]

    model_config = {"from_attributes": True}


class LeaveRequestCreate(BaseModel):
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveRequestOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StaffingRequirementCreate(BaseModel):
    location_id: int
    skill_id: Optional[int] = None
    day_of_week: int = Field(ge=0, le=6)
    start_time: str
    end_time: str
    min_staff: int = Field(ge=1)


class StaffingRequirementOut(BaseModel):
    id: int
    location_id: int
    skill_id: Optional[int]
    day_of_week: int
    start_time: str
    end_time: str
    min_staff: int

    model_config = {"from_attributes": True}


class ScheduleGenerateRequest(BaseModel):
    location_id: int
    start_date: date
    end_date: date
    weights: Optional[dict] = None


class ShiftOut(BaseModel):
    id: int
    employee_id: int
    skill_id: Optional[int]
    date: date
    start_time: str
    end_time: str
    is_opening: bool
    is_closing: bool

    model_config = {"from_attributes": True}


class ScheduleOut(BaseModel):
    id: int
    location_id: int
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    published_at: Optional[datetime]
    shifts: List[ShiftOut] = []

    model_config = {"from_attributes": True}


class ScheduleConflict(BaseModel):
    type: str
    message: str
    employee_id: Optional[int] = None
    date: Optional[date] = None


class ScheduleGenerateResponse(BaseModel):
    schedule: Optional[ScheduleOut] = None
    feasible: bool
    conflicts: List[ScheduleConflict] = []
    explanations: List[str] = []


class ShiftSwapCreate(BaseModel):
    shift_id: int
    target_employee_id: Optional[int] = None


class ShiftSwapOut(BaseModel):
    id: int
    shift_id: int
    source_employee_id: int
    target_employee_id: Optional[int]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
