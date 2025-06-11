from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.schemas.address import AddressCreate, AddressUpdate, AddressOut

class PatientCreate(BaseModel):
    """Data required to register a new patient."""
    first_name: str
    last_name: str
    email: str
    phone_number: str
    date_of_birth: date
    gender: str
    allergies: Optional[str] = None
    past_illnesses: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[AddressCreate] = None

class PatientOut(BaseModel):
    """Basic patient data shown in lists or previews."""
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
    """Extended patient detail including medical info."""
    date_of_birth: date
    gender: str
    allergies: Optional[str] = None
    past_illnesses: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    """Fields that can be updated for a patient."""
    assigned_user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    allergies: Optional[str] = None
    past_illnesses: Optional[str] = None
    current_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[AddressUpdate] = None

class DoctorSummary(BaseModel):
    """Minimal representation of a doctor assigned to a patient."""
    id: int
    title: Optional[str]
    first_name: str
    last_name: str
    email: str

    model_config = {"from_attributes": True}

class PatientWithDoctor(PatientDetail):
    """Extended patient detail including assigned doctor info."""
    assigned_doctor: DoctorSummary

