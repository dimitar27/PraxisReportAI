from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    password: str
    role: str  # "admin", "doctor", "assistant"
    title: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    role: Optional[str]
    title: Optional[str]

class PasswordReset(BaseModel):
    new_password: str