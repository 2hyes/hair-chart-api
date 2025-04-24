from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String(20), unique=True)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"))
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"))
    memo = Column(String)
