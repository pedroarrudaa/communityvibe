from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    company: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 