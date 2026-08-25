from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime


class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key= True, autoincrement= True)
    name = Column(String(100), nullable= False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable= False)
    created_at = Column(DateTime, default= lambda : datetime.now(), nullable= False)

    user = relationship("UserModel", back_populates= "events")
    event_staff = relationship("EventStaffModel", back_populates= "events", cascade="all, delete-orphan")
    tasks = relationship("EventTaskModel", back_populates= "event", cascade="all, delete-orphan")

class EventStaffModel(Base):
    __tablename__ = "event_staff"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key= True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key= True)
    role = Column(Enum("OWNER", "MEMBER"), default= "MEMBER") # OWNER hoặc MEMBER
    joined_at = Column(DateTime, default= lambda : datetime.now(), nullable= False)

    users = relationship("UserModel", back_populates= "event_staff")
    events = relationship("EventModel", back_populates= "event_staff")