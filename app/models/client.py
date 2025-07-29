from sqlalchemy import Column, Integer, BigInteger, String, Boolean
from app.models.base import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String)
    phone_number = Column(String)
    admin = Column(Boolean, default=False, nullable=False)