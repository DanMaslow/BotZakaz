from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client")
    time_slot = relationship("TimeSlot")