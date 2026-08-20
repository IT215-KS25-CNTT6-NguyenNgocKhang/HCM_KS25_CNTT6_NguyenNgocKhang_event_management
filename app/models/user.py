from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True, autoincrement= True)
    email = Column(String(255), unique= True, nullable= False)
    password_hash = Column(String(255), nullable= False)
    full_name = Column(String(100), nullable= False)
    role = Column(Enum("USER", "ADMIN"), default= "USER") # USER hoặc ADMIN
    is_active = Column(Boolean, default= True)
    create_at = Column(DateTime, default= lambda : datetime.now(),nullable= False)

    events = relationship("EventModel", back_populates= "user")
    event_staff = relationship("EventStaffModel", back_populates= "users")
    tasks = relationship("EventTaskModel", back_populates= "assignee")