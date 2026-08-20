from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email : EmailStr
    full_name : str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id : int
    role : str = "USER"
    is_active : bool
    create_at : datetime

    model_config = ConfigDict(from_attributes= True)