"""Authentication, security, and multi-tenancy utilities."""
import hashlib
import secrets
from datetime import timedelta
from typing import Optional, Callable, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

security = HTTPBearer()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_val = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${hash_val}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3 or parts[0] != "sha256":
            return False
        salt, stored_hash = parts[1], parts[2]
        computed = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return secrets.compare_digest(computed, stored_hash)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    from datetime import datetime
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    from app.models.models import User

    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_role(*roles: str):
    """Dependency to check if the current user has the required role."""
    def role_checker(current_user: "User" = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_business_owner():
    """Dependency to check if the current user is a business owner."""
    def owner_checker(current_user: "User" = Depends(get_current_user)):
        if current_user.role.value != "business_owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Only business owners can perform this action"
            )
        return current_user
    return owner_checker

def require_manager_or_owner():
    """Dependency to check if the current user is a manager or business owner."""
    def manager_checker(current_user: "User" = Depends(get_current_user)):
        if current_user.role.value not in ["business_owner", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Only managers or business owners can perform this action"
            )
        return current_user
    return manager_checker

def require_employee():
    """Dependency to check if the current user is an employee."""
    def employee_checker(current_user: "User" = Depends(get_current_user)):
        if current_user.role.value != "employee":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Only employees can perform this action"
            )
        return current_user
    return employee_checker


def get_business_id(current_user: "User" = Depends(get_current_user)) -> int:
    """Get the business ID of the current user."""
    return current_user.business_id
