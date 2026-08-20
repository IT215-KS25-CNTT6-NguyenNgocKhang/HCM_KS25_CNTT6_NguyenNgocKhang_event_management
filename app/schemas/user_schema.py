from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email : EmailStr
    full_name : str

class UserCreate(UserBase):
    role : str
    is_active : bool
    create_at : datetime

class UserUpdate(BaseModel):
    email : Optional[str] = None
    full_name : Optional[str] = None
    role : Optional[str] = None
    is_active : Optional[bool] = None
    create_at : Optional[datetime] = None


class UserResponse(UserBase):
    id : int
    role : str = "USER"
    is_active : bool
    create_at : datetime

    model_config = ConfigDict(from_attributes= True)