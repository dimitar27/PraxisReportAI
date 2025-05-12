from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # doctor|assistant|admin
    title = Column(String, nullable=True)
    specialization = Column(String)
    practice_name = Column(String)

    profile = relationship("Profile", back_populates="user", uselist=False)
    patients = relationship("Patient", back_populates="doctor")