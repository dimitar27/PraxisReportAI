from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserCreate
from app.models.user import User
from app.models.profile import Profile
from app.core.security import get_password_hash, require_admin
from app.core.security import admin_only
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from fastapi import status

router = APIRouter()

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

