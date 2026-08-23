from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email : EmailStr = Field(min_length= 1)

class UserCreate(UserBase):
    full_name : str = Field(min_length= 5)
    password: str = Field(min_length= 6)
    role : str = "USER"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role : Optional[str] = None
    is_active : Optional[bool] = None

class UserLogin(UserBase):
    password: str = Field(min_length= 6)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)