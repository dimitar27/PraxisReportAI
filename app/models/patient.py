from sqlalchemy import Column, Integer, Date, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Patient(Base, TimestampMixin):
    """
    Represents a patient in the system. Each patient has a profile and may have multiple medical reports.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String)
    allergies = Column(Text)
    pre_diagnosis = Column(Text)
    current_diagnosis = Column(Text)
    notes = Column(Text)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="patient")
    doctor  = relationship("User", back_populates="patients")
    reports = relationship("MedicalReport", back_populates="patient")
