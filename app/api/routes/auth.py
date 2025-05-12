from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate
from app.models.user import User
from app.models.profile import Profile
from app.core.security import get_password_hash, require_admin
from app.core.security import admin_only
from typing import Optional

router = APIRouter()

@router.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(admin_only)
):
    # Check if email already exists
    existing_profile = db.query(Profile).filter_by(email=user_data.email).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    # Create profile
    profile = Profile(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number
    )
    db.add(profile)
    db.flush()  # Gets profile.id before commit

    # Determine title
    title = user_data.title if user_data.title else ("Dr. med." if user_data.role == "doctor" else "")

    # Create user
    user = User(
        profile_id=profile.id,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        title=title
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": f"{user.role.capitalize()} account created",
        "user_id": user.id
    }

from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from fastapi import status

@router.post("/signin")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by email (OAuth2 expects username field)
    user = (
        db.query(User)
        .join(Profile)
        .filter(Profile.email == form_data.username)
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {
        "sub": str(user.id),
        "role": user.role
    }

    token = create_access_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

