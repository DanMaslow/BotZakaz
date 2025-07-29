from sqlalchemy import Column, Integer, BigInteger, String
from app.models.base import Base  # <== вот это важно

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String)
    phone_number = Column(String)