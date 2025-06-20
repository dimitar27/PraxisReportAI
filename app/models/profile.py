from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Profile(Base, TimestampMixin):
    """
    Stores personal details like name, email, and phone number.
    Shared by both users (doctors/assistants) and patients.
    """
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String)

    # Relationships
    user = relationship("User", back_populates="profile", uselist=False)
    patient = relationship("Patient", back_populates="profile", uselist=False)
    addresses = relationship(
        "Address",
        back_populates="profile",
        cascade="all, delete-orphan"
    )