# app/models/profile.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String)

    user = relationship("User", back_populates="profile", uselist=False)
    patient = relationship("Patient", back_populates="profile", uselist=False)
    addresses = relationship("Address", back_populates="profile")