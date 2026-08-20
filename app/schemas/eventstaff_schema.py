from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EventStaffBase(BaseModel):
    event_id : int
    user_id : int

class EventStaffCreate(EventStaffBase):
    role : str
    joined_at : datetime

class EventStaffUpdate(BaseModel):
    event_id : Optional[int] = None
    user_id : Optional[int] = None
    role : Optional[str] = None
    joined_at : Optional[datetime] = None

class EventStaffResponse(EventStaffBase):
    role : str
    joined_at : datetime

    model_config = ConfigDict(from_attributes= True)