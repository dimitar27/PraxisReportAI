from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """
    Represents a user of the system (e.g. doctor, assistant, admin).
    Contains login credentials and role-based info.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    password_hash = Column(String, nullable=False) # Securely hashed password
    role = Column(String, nullable=False)  # doctor|assistant|admin
    title = Column(String, nullable=True) # Optional professional title (e.g., "Dr. med.", "Prof.")
    specialization = Column(String) # Area of medical specialization (e.g., Neurology, Psychiatry)
    practice_name = Column(String)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    patients = relationship("Patient", back_populates="doctor")