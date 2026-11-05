"""Business, location, and user models."""
from __future__ import annotations

import enum
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"


class UserRole(str, enum.Enum):
    BUSINESS_OWNER = "business_owner"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CASUAL = "casual"
    TEMPORARY = "temporary"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    status: Mapped[BusinessStatus] = mapped_column(SAEnum(BusinessStatus), default=BusinessStatus.TRIAL)
    timezone: Mapped[str] = mapped_column(String(100), default="Asia/Kathmandu")
    currency: Mapped[str] = mapped_column(String(3), default="NPR")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    locations: Mapped[List["Location"]] = relationship("Location", back_populates="business", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="business", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    business: Mapped["Business"] = relationship("Business", back_populates="locations")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    business: Mapped["Business"] = relationship("Business", back_populates="users")
    employee: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="user", uselist=False)

    __table_args__ = (UniqueConstraint("business_id", "email", name="uq_business_email"),)


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("business_id", "name", name="uq_business_skill"),)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    employment_type: Mapped[EmploymentType] = mapped_column(SAEnum(EmploymentType), default=EmploymentType.FULL_TIME)
    hourly_wage: Mapped[float] = mapped_column(Float, default=0.0)
    position: Mapped[Optional[str]] = mapped_column(String(200))
    contractual_hours_per_week: Mapped[float] = mapped_column(Float, default=40.0)
    max_hours_per_week: Mapped[float] = mapped_column(Float, default=48.0)
    min_hours_per_week: Mapped[float] = mapped_column(Float, default=0.0)
    max_consecutive_days: Mapped[int] = mapped_column(Integer, default=6)
    min_rest_hours_between_shifts: Mapped[float] = mapped_column(Float, default=11.0)
    preferred_days: Mapped[Optional[str]] = mapped_column(String(100))
    unavailable_days: Mapped[Optional[str]] = mapped_column(String(100))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="employee")
    skills: Mapped[List["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    availability: Mapped[List["Availability"]] = relationship("Availability", back_populates="employee", cascade="all, delete-orphan")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill")

    __table_args__ = (UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),)


class Availability(Base):
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5))
    end_time: Mapped[Optional[str]] = mapped_column(String(5))
    note: Mapped[Optional[str]] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="availability")

    __table_args__ = (UniqueConstraint("employee_id", "date", name="uq_employee_date_availability"),)


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[LeaveStatus] = mapped_column(SAEnum(LeaveStatus), default=LeaveStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests")


class ScheduleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(SAEnum(ScheduleStatus), default=ScheduleStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    shifts: Mapped[List["Shift"]] = relationship("Shift", back_populates="schedule", cascade="all, delete-orphan")


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("skills.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    is_opening: Mapped[bool] = mapped_column(Boolean, default=False)
    is_closing: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="shifts")
    employee: Mapped["Employee"] = relationship("Employee")
    skill: Mapped[Optional["Skill"]] = relationship("Skill")


class StaffingRequirement(Base):
    __tablename__ = "staffing_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(Integer, ForeignKey("businesses.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    skill_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("skills.id"), nullable=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    min_staff: Mapped[int] = mapped_column(Integer, default=1)


class ShiftSwapStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ShiftSwap(Base):
    __tablename__ = "shift_swaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shift_id: Mapped[int] = mapped_column(Integer, ForeignKey("shifts.id"), nullable=False)
    source_employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    target_employee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"), nullable=True)
    status: Mapped[ShiftSwapStatus] = mapped_column(SAEnum(ShiftSwapStatus), default=ShiftSwapStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    shift: Mapped["Shift"] = relationship("Shift")
    source_employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[source_employee_id])
    target_employee: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[target_employee_id])
