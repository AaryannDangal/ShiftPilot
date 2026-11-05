"""Scheduling routes, generation, publishing, and shift swaps."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Availability,
    Business,
    Employee,
    LeaveRequest,
    Schedule,
    ScheduleStatus,
    Shift,
    ShiftSwap,
    ShiftSwapStatus,
    StaffingRequirement,
    User,
    UserRole,
)
from app.schemas.schemas import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleOut,
    ShiftSwapCreate,
    ShiftSwapOut,
)
from app.security import get_current_user
from app.services.scheduler import generate_optimized_schedule

router = APIRouter(prefix="/api/v1/scheduling", tags=["scheduling"])


@router.post("/generate", response_model=ScheduleGenerateResponse)
def generate_schedule(
    payload: ScheduleGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.BUSINESS_OWNER, UserRole.MANAGER):
        raise HTTPException(status_code=403, detail="Permission denied")

    employees = db.query(Employee).filter(Employee.business_id == current_user.business_id, Employee.is_active == True).all()
    requirements = db.query(StaffingRequirement).filter(
        StaffingRequirement.business_id == current_user.business_id,
        StaffingRequirement.location_id == payload.location_id,
    ).all()
    availabilities = db.query(Availability).filter(
        Availability.employee_id.in_([e.id for e in employees]),
        Availability.date >= payload.start_date,
        Availability.date <= payload.end_date,
    ).all()
    leave_requests = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id.in_([e.id for e in employees]),
        LeaveRequest.status.value == "approved",
    ).all()

    feasible, shifts, explanations, conflicts = generate_optimized_schedule(
        employees=employees,
        requirements=requirements,
        availabilities=availabilities,
        leave_requests=leave_requests,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    schedule_out = None
    if feasible:
        schedule = Schedule(
            business_id=current_user.business_id,
            location_id=payload.location_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=ScheduleStatus.DRAFT,
        )
        db.add(schedule)
        db.flush()

        for s in shifts:
            db.add(Shift(
                schedule_id=schedule.id,
                employee_id=s["employee_id"],
                skill_id=s["skill_id"],
                date=s["date"],
                start_time=s["start_time"],
                end_time=s["end_time"],
                is_opening=s["is_opening"],
                is_closing=s["is_closing"],
            ))
        db.commit()
        db.refresh(schedule)
        schedule_out = ScheduleOut.model_validate(schedule)

    return ScheduleGenerateResponse(
        schedule=schedule_out,
        feasible=feasible,
        conflicts=conflicts,
        explanations=explanations,
    )


@router.post("/schedules/{schedule_id}/publish", response_model=ScheduleOut)
def publish_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.BUSINESS_OWNER, UserRole.MANAGER):
        raise HTTPException(status_code=403, detail="Permission denied")

    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.business_id == current_user.business_id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.status = ScheduleStatus.PUBLISHED
    schedule.published_at = datetime.utcnow()
    db.commit()
    db.refresh(schedule)
    return ScheduleOut.model_validate(schedule)


@router.get("/schedules", response_model=list[ScheduleOut])
def list_schedules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    schedules = db.query(Schedule).filter(Schedule.business_id == current_user.business_id).all()
    return [ScheduleOut.model_validate(s) for s in schedules]


@router.get("/schedules/{schedule_id}", response_model=ScheduleOut)
def get_schedule(schedule_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.business_id == current_user.business_id,
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleOut.model_validate(schedule)


@router.post("/shifts/{shift_id}/swap", response_model=ShiftSwapOut, status_code=201)
def request_shift_swap(
    shift_id: int,
    payload: ShiftSwapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.employee_profile:
        raise HTTPException(status_code=400, detail="User has no employee profile")

    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    swap = ShiftSwap(
        shift_id=shift.id,
        source_employee_id=current_user.employee_profile.id,
        target_employee_id=payload.target_employee_id,
        status=ShiftSwapStatus.PENDING,
    )
    db.add(swap)
    db.commit()
    db.refresh(swap)
    return ShiftSwapOut.model_validate(swap)
