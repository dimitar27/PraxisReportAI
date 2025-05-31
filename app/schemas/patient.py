from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.schemas.address import AddressCreate, AddressUpdate, AddressOut

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    date_of_birth: date
    gender: str
    allergies: Optional[str] = None
    pre_diagnosis: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[AddressCreate] = None

class PatientOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: Optional[AddressOut] = None

    model_config = {
        "from_attributes": True
    }

class PatientDetail(PatientOut):
    date_of_birth: date
    gender: str
    allergies: Optional[str] = None
    pre_diagnosis: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    assigned_user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    allergies: Optional[str] = None
    pre_diagnosis: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[AddressUpdate] = None

class DoctorSummary(BaseModel):
    id: int
    title: Optional[str]
    first_name: str
    last_name: str
    email: str

    model_config = {"from_attributes": True}

class PatientWithDoctor(PatientDetail):
    assigned_doctor: DoctorSummary

