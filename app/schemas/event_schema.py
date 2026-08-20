from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    name : str
    description: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)