from fastapi import APIRouter, HTTPException
from app.models import Address
from app.models.profile import Profile
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, require_admin
from app.core.security import admin_only
from app.schemas.user import UserUpdate
from app.schemas.user import PasswordReset
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    if db.query(Profile).filter_by(email=user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    profile = Profile(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )
    db.add(profile)
    db.flush()

    title = user_data.title or ("Dr. med." if user_data.role == "doctor" else "")

    user = User(
        profile_id=profile.id,
        role=user_data.role,
        password_hash=get_password_hash(user_data.password),
        title=title
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "user_id": user.id}

@router.get("/debug/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []

    for user in users:
        profile = user.profile
        address = profile.addresses[0] if profile.addresses else None

        user_data = {
            "id": user.id,
            "email": profile.email,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "phone_number": profile.phone_number,
            "role": user.role,
            "title": user.title,
        }

        if address:
            user_data["address"] = {
                "street": address.street,
                "postal_code": address.postal_code,
                "city": address.city,
                "country": address.country
            }

        result.append(user_data)

    return result

@router.get("/me")
def read_own_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "role": current_user.role,
        "title": current_user.title
    }

@router.patch("/users/{user_id}")
def update_user_partial(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    for key in ["role", "title"]:
        value = getattr(user_update, key)
        if value is not None:
            setattr(user, key, value)

    # Update profile fields
    for key in ["email", "first_name", "last_name", "phone_number"]:
        value = getattr(user_update, key)
        if value is not None:
            setattr(user.profile, key, value)

    # Update or create address
    address = None
    if user_update.address:
        address = user.profile.addresses[0] if user.profile.addresses else None
        if not address:
            address = Address(profile_id=user.profile.id)
            db.add(address)

        for field, value in user_update.address.dict(exclude_unset=True).items():
            setattr(address, field, value)

    db.commit()
    db.refresh(user)

    # Prepare address dict if it exists
    address_data = None
    if user.profile.addresses:
        addr = user.profile.addresses[0]
        address_data = {
            "street": addr.street,
            "postal_code": addr.postal_code,
            "city": addr.city,
            "country": addr.country
        }

    return {
        "id": user.id,
        "email": user.profile.email,
        "first_name": user.profile.first_name,
        "last_name": user.profile.last_name,
        "phone_number": user.profile.phone_number,
        "role": user.role,
        "title": user.title,
        "address": address_data
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="You cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Also delete the associated profile
    profile = user.profile
    db.delete(user)
    if profile:
        db.delete(profile)

    db.commit()
    return {"message": f"User {user_id} and profile deleted"}

@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    password_data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to reset a user's password.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": f"Password for user {user_id} has been reset"}