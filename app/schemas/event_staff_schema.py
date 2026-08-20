from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EventStaffBase(BaseModel):
    role: str = "MEMBER"

class EventStaffCreate(EventStaffBase):
    user_id: int
    
class EventStaffResponse(EventStaffBase):
    event_id: int
    user_id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)