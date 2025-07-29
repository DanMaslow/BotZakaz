from sqlalchemy import Column, Integer, Date, Time, Boolean
from app.db.base import Base

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    is_booked = Column(Boolean, default=False)