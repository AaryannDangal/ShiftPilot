"""Authentication and business registration routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Business, BusinessStatus, User, UserRole, Location
from app.schemas.schemas import (
    BusinessCreate,
    BusinessOut,
    LoginRequest,
    LocationCreate,
    LocationOut,
    TokenOut,
    UserCreate,
    UserOut,
)
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_business_owner,
    require_manager_or_owner,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def slugify(name: str) -> str:
    return name.lower().strip().replace(" ", "-")


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register_business(
    business_name: str,
    business_timezone: str,
    business_currency: str,
    user_email: str,
    user_password: str,
    user_full_name: str,
    db: Session = Depends(get_db),
):
    """Flat registration: create business + owner user in one call."""
    import re
    if re.search(r'[<>,\'"\\]', business_name):
        raise HTTPException(status_code=400, detail="Invalid business name")

    existing = db.query(Business).filter(Business.name == business_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Business name already taken")

    business = Business(
        name=business_name,
        slug=slugify(business_name),
        status=BusinessStatus.TRIAL,
        timezone=business_timezone,
        currency=business_currency,
    )
    db.add(business)
    db.flush()

    user = User(
        business_id=business.id,
        email=user_email.lower(),
        hashed_password=hash_password(user_password),
        full_name=user_full_name,
        role=UserRole.BUSINESS_OWNER,
    )
    db.add(user)

    default_location = Location(business_id=business.id, name="Main Location")
    db.add(default_location)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.get("/business", response_model=BusinessOut)
def get_business(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == current_user.business_id).first()
    return BusinessOut.model_validate(business)


@router.post("/locations", response_model=LocationOut, status_code=201)
def create_location(
    payload: LocationCreate,
    current_user: User = Depends(require_manager_or_owner()),
    db: Session = Depends(get_db),
):
    location = Location(business_id=current_user.business_id, name=payload.name, address=payload.address)
    db.add(location)
    db.commit()
    db.refresh(location)
    return LocationOut.model_validate(location)


@router.get("/locations", response_model=list[LocationOut])
def list_locations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    locations = db.query(Location).filter(
        Location.business_id == current_user.business_id,
        Location.is_active == True,
    ).all()
    return [LocationOut.model_validate(loc) for loc in locations]


@router.post("/invite-manager", response_model=UserOut, status_code=201)
def invite_manager(
    payload: UserCreate,
    current_user: User = Depends(require_business_owner()),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    manager = User(
        business_id=current_user.business_id,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=UserRole.MANAGER,
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return UserOut.model_validate(manager)
