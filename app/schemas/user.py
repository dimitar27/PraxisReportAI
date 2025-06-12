from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

from app.schemas.address import AddressCreate, AddressUpdate

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

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """
        Validates that the password meets minimum strength requirements.

        Requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Raises:
            ValueError: If the password does not meet the criteria.

        Returns:
            str: The validated password string.
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one digit")
        if not re.search(r"[^\w\s]", value):
            raise ValueError("Password must include at least one special character")
        return value

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

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        """
        Ensures the new password meets defined complexity rules.

        Requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Raises:
            ValueError: If the password is too weak.

        Returns:
            str: The validated new password.
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one digit")
        if not re.search(r"[^\w\s]", value):
            raise ValueError("Password must include at least one special character")
        return value