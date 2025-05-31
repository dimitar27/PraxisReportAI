from pydantic import BaseModel
from typing import Optional
from app.schemas.address import AddressCreate
from app.schemas.address import AddressUpdate

class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    password: str
    role: str  # "admin", "doctor", "assistant"
    title: Optional[str] = None
    address: Optional[AddressCreate] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
    address: Optional[AddressUpdate] = None

class PasswordReset(BaseModel):
    new_password: str