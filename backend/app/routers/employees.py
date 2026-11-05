"""Employee management, skills, availability, and leave routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Availability,
    Employee,
    EmployeeSkill,
    LeaveRequest,
    LeaveStatus,
    Skill,
    User,
    UserRole,
)
from app.schemas.schemas import (
    AvailabilityCreate,
    AvailabilityOut,
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    LeaveRequestCreate,
    LeaveRequestOut,
    SkillCreate,
    SkillOut,
)
from app.security import (
    get_current_user,
    get_business_id,
    require_business_owner,
    require_employee,
    require_manager_or_owner,
)

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


@router.post("/skills", response_model=SkillOut, status_code=201)
def create_skill(
    payload: SkillCreate,
    current_user: User = Depends(require_manager_or_owner()),
    db: Session = Depends(get_db),
):
    skill = Skill(business_id=current_user.business_id, name=payload.name, description=payload.description)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return SkillOut.model_validate(skill)


@router.get("/skills", response_model=list[SkillOut])
def list_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skills = db.query(Skill).filter(Skill.business_id == current_user.business_id).all()
    return [SkillOut.model_validate(s) for s in skills]


@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(require_manager_or_owner()),
    db: Session = Depends(get_db),
):
    employee = Employee(
        business_id=current_user.business_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        employment_type=payload.employment_type,
        hourly_wage=payload.hourly_wage,
        position=payload.position,
        contractual_hours_per_week=payload.contractual_hours_per_week,
        max_hours_per_week=payload.max_hours_per_week,
        min_hours_per_week=payload.min_hours_per_week,
        max_consecutive_days=payload.max_consecutive_days,
        min_rest_hours_between_shifts=payload.min_rest_hours_between_shifts,
        preferred_days=payload.preferred_days,
        unavailable_days=payload.unavailable_days,
        start_date=payload.start_date,
    )
    db.add(employee)
    db.flush()

    for skill_id in payload.skill_ids:
        es = EmployeeSkill(employee_id=employee.id, skill_id=skill_id)
        db.add(es)

    db.commit()
    db.refresh(employee)
    return EmployeeOut.from_orm(employee)


@router.get("/", response_model=list[EmployeeOut])
def list_employees(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Employee).filter(Employee.business_id == current_user.business_id)
    if current_user.role == UserRole.EMPLOYEE:
        query = query.filter(Employee.user_id == current_user.id)
    employees = query.all()
    return [EmployeeOut.from_orm(e) for e in employees]


@router.post("/availability", response_model=AvailabilityOut, status_code=201)
def set_availability(
    payload: AvailabilityCreate,
    current_user: User = Depends(require_employee()),
    db: Session = Depends(get_db),
):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id, Employee.business_id == current_user.business_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing = db.query(Availability).filter(
        Availability.employee_id == payload.employee_id,
        Availability.date == payload.date,
    ).first()

    if existing:
        existing.is_available = payload.is_available
        existing.start_time = payload.start_time
        existing.end_time = payload.end_time
        existing.note = payload.note
        db.commit()
        db.refresh(existing)
        return AvailabilityOut.model_validate(existing)

    avail = Availability(
        employee_id=payload.employee_id,
        date=payload.date,
        is_available=payload.is_available,
        start_time=payload.start_time,
        end_time=payload.end_time,
        note=payload.note,
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    return AvailabilityOut.model_validate(avail)


@router.post("/leave", response_model=LeaveRequestOut, status_code=201)
def request_leave(
    payload: LeaveRequestCreate,
    current_user: User = Depends(require_employee()),
    db: Session = Depends(get_db),
):
    if not current_user.employee_profile:
        raise HTTPException(status_code=400, detail="User is not linked to an employee profile")

    leave = LeaveRequest(
        employee_id=current_user.employee_profile.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return LeaveRequestOut.model_validate(leave)


@router.get("/leave", response_model=list[LeaveRequestOut])
def list_leave_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role in (UserRole.BUSINESS_OWNER, UserRole.MANAGER):
        leaves = db.query(LeaveRequest).join(Employee).filter(Employee.business_id == current_user.business_id).all()
    else:
        if not current_user.employee_profile:
            return []
        leaves = db.query(LeaveRequest).filter(LeaveRequest.employee_id == current_user.employee_profile.id).all()
    return [LeaveRequestOut.model_validate(l) for l in leaves]


@router.patch("/leave/{leave_id}", response_model=LeaveRequestOut)
def update_leave_status(
    leave_id: int,
    status_val: str,
    current_user: User = Depends(require_manager_or_owner()),
    db: Session = Depends(get_db),
):
    leave = db.query(LeaveRequest).join(Employee).filter(
        LeaveRequest.id == leave_id,
        Employee.business_id == current_user.business_id,
    ).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = LeaveStatus(status_val)
    db.commit()
    db.refresh(leave)
    return LeaveRequestOut.model_validate(leave)
