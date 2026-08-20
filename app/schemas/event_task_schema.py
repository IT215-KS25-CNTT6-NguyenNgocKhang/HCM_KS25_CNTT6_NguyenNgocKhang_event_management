from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EventTaskBase(BaseModel):
    event_id : int
    assignee_id : int

class EventTaskCreate(EventTaskBase):
    title : str
    description : str
    status : str
    priority : str
    due_date : datetime
    created_at : datetime

class EventTaskUpdate(BaseModel):
    event_id : Optional[int] = None
    assignee_id : Optional[int] = None
    title : Optional[str] = None
    description : Optional[str] = None
    status : Optional[str] = None
    priority : Optional[str] = None
    due_date : Optional[datetime] = None
    created_at : Optional[datetime] = None

class EventTaskResponse(EventTaskBase):
    title : str
    description : str
    status : str
    priority : str
    due_date : datetime
    created_at : datetime

    model_config = ConfigDict(from_attributes= True)