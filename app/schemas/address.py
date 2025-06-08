from pydantic import BaseModel
from typing import Optional

class AddressCreate(BaseModel):
    """Data required to create a new address."""
    street: str
    postal_code: str
    city: str
    country: str

class AddressUpdate(BaseModel):
    """Fields that can be updated for an address."""
    street: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    country: Optional[str]

class AddressOut(BaseModel):
    """Address representation returned in API responses."""
    street: str
    postal_code: str
    city: str
    country: str

    model_config = {"from_attributes": True}