from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Address(Base, TimestampMixin):
    """
    Represents a physical address associated with a profile.
    Used for both patients and doctors.
    """
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    street = Column(String)
    postal_code = Column(String)
    city = Column(String)
    country = Column(String)

    # Link to associated profile
    profile = relationship("Profile", back_populates="addresses")
