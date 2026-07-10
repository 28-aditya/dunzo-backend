from pydantic import BaseModel, EmailStr
from typing import Optional


class UserStateUpdate(BaseModel):
    current_view: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
