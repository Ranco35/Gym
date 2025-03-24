from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    name = Column(String)
    exercises = Column(JSON)
    metrics = Column(JSON)
    notes = Column(String)
    
    user = relationship("User", back_populates="workouts")