from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import verify_password, create_access_token
from app.models.profile import Profile
from app.models.user import User

router = APIRouter()

# Endpoint: User login
@router.post("/signin")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Authenticates a user using OAuth2 form data (username and password) and returns a JWT token.

    Parameters:
    - form_data: OAuth2 form input containing 'username' (email) and 'password'
    - db: Database session

    Returns:
    - A bearer token (JWT) to be used for authenticated requests

    Raises:
    - HTTP 401 if user is not found or password is incorrect
    """

    # Find user by email (OAuth2 expects username field)
    user = (
        db.query(User)
        .join(Profile)
        .filter(Profile.email == form_data.username)
        .first()
    )

    # Verify if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Token payload includes user ID and role
    token_data = {
        "sub": str(user.id),
        "role": user.role
    }

    # Generate JWT access token
    token = create_access_token(token_data)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
