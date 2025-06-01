from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicalReportCreate(BaseModel):
    title: str
    patient_history: str
    physical_exam: str

class MedicalReportUpdate(BaseModel):
    title: Optional[str] = None
    patient_history: Optional[str] = None
    physical_exam: Optional[str] = None
    final_report: Optional[str] = None

class MedicalReportOut(BaseModel):
    id: int
    patient_id: int
    title: str
    patient_history: Optional[str]
    physical_exam: Optional[str]
    final_report: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}