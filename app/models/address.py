# app/models/address.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    street = Column(String)
    postal_code = Column(String)
    city = Column(String)
    country = Column(String)

    profile = relationship("Profile", back_populates="addresses")
