from pydantic import BaseModel
from typing import Optional

class AddressCreate(BaseModel):
    street: str
    postal_code: str
    city: str
    country: str

class AddressUpdate(BaseModel):
    street: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    country: Optional[str]

class AddressOut(BaseModel):
    street: str
    postal_code: str
    city: str
    country: str

    model_config = {"from_attributes": True}