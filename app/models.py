from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users" # user_type: customer, shop, designer
    
    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    memo = Column(String, nullable=True)
    user_type = Column(String(10), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

class Shop(Base):
    __tablename__ = "shops"

    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    number = Column(String(20), nullable=False)
    biz_number = Column(String(20), nullable=False)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    memo = Column(String)
