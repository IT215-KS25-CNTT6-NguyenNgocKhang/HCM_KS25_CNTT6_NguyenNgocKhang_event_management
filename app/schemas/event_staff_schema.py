from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EventStaffBase(BaseModel):
    pass

class EventStaffCreate(EventStaffBase):
    user_id: int
    
class EventStaffResponse(EventStaffBase):
    event_id: int
    user_id: int
    role: str = "MEMBER"
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)