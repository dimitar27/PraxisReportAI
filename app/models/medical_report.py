from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class MedicalReport(Base, TimestampMixin):
    """
    Represents a medical report for a patient, typically generated via AI.
    Includes exam details, history, and the final report.
    """
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    title = Column(String, nullable=False)
    patient_history = Column(Text)
    physical_exam = Column(Text)
    final_report = Column(Text)

    # Link to the patient that owns this report
    patient = relationship("Patient", back_populates="reports")
