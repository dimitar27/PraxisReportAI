from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User

# OAuth2 scheme used to extract and validate bearer token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

# Secret used to sign the JWT token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #for password hashing


def get_password_hash(password: str) -> str:
    """Returns a hashed version of the input password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodes the JWT token and retrieves the current user from the database.

    Raises:
    - 401 Unauthorized if the token is invalid
    - 404 Not Found if user is not in the database
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def admin_only(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency that allows only admin users to proceed.

    Raises:
    - 401 Unauthorized if token is invalid
    - 403 Forbidden if user is not an admin
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")

    return user


def require_doctor_or_admin(user: User = Depends(get_current_user)) -> User:
    """
    Dependency that allows only doctors or admins to proceed.

    Raises:
    - 403 Forbidden if user is neither doctor nor admin
    """
    if user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Doctor or admin privileges required")
    return user


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a JWT access token for the given data payload.

    Parameters:
    - data: A dictionary of claims to include in the token (e.g. user ID, role)
    - expires_delta: Optional timedelta for custom expiration

    Returns:
    - A JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt