
from datetime import datetime, timedelta, timezone
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from Database import get_db
from Models import User


# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Set it in your environment before starting."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Hash a password
def hash_password(password: str) -> str:
    return password_context.hash(password)


# Verify a password
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_context.verify(
        plain_password,
        hashed_password
    )


# Create JWT access token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# Get the currently authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        token_role = payload.get("role")

        if user_id is None or token_role is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise credentials_exception

    # Check that the role in the token is still current
    if user.role != token_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User role changed. Please log in again."
        )

    return user


# Role-based access control
def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker


# Employee-only access
employee_only = require_roles("EMPLOYEE")

# HR-only access
hr_only = require_roles("HR")

# Admin-only access
admin_only = require_roles("ADMIN")

# HR and Admin access
hr_or_admin = require_roles("HR", "ADMIN")

# All authenticated roles
authenticated_user = require_roles(
    "EMPLOYEE", "HR", "ADMIN"
)
