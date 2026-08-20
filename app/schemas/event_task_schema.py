from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "LOW" 
    due_date: Optional[datetime] = None

class EventTaskCreate(EventTaskBase):
    assignee_id: Optional[int] = None

class EventTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None  # TODO / IN_PROGRESS / DONE
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)