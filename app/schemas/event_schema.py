from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    name : str

class EventCreate(EventBase):
    description : str
    owner_id : int
    create_at : datetime

class EventUpdate(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    owner_id : Optional[int] = None
    create_at : Optional[datetime] = None

class EventResponse(EventBase):
    description : str
    owner_id : int
    create_at : datetime

    model_config = ConfigDict(from_attributes= True)