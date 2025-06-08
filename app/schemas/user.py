from pydantic import BaseModel
from typing import Optional
from app.schemas.address import AddressCreate
from app.schemas.address import AddressUpdate

class UserCreate(BaseModel):
    """Data required to create a new user (admin, doctor, or assistant)."""
    email: str
    first_name: str
    last_name: str
    phone_number: str
    password: str
    role: str  # "admin", "doctor", "assistant"
    title: Optional[str] = None
    specialization: Optional[str] = None
    practice_name: Optional[str] = None
    address: AddressCreate # Required practice address

class UserUpdate(BaseModel):
    """Fields that can be updated for a user."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
    specialization: Optional[str] = None
    practice_name: Optional[str] = None
    address: Optional[AddressUpdate] = None

class PasswordReset(BaseModel):
    """Schema for resetting a user's password."""
    new_password: str