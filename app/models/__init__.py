# app/models/__init__.py

from .base import Base
from .user import User
from .profile import Profile
from .patient import Patient
from .medical_report import MedicalReport
from .address import Address

# so that `Base.metadata` includes all tables:
__all__ = ["Base", "User", "Profile", "Patient", "MedicalReport", "Address"]
