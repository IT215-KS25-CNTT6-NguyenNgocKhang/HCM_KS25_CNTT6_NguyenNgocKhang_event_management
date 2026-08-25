from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

class EventTaskModel(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key= True, autoincrement= True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable= False)
    title = Column(String(255), nullable= False)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable= True)
    status = Column(Enum("TODO", "IN_PROGRESS", "DONE"), default= "TODO") # TO DO hoặc "IN_PROGRESS" hoặc "DONE"
    priority = Column(Enum("LOW", "MEDIUM", "HIGH"), default= "LOW") # LOW / MEDIUM / HIGH
    due_date = Column(DateTime)
    created_at = Column(DateTime, default= lambda : datetime.now(), nullable= False)

    event = relationship("EventModel", back_populates= "tasks")
    assignee = relationship("UserModel", back_populates= "tasks")