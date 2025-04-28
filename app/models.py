from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String(20), unique=True)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    memo = Column(String)


class UserHairProfile(Base):
    __tablename__ = "user_hair_profile"

    seq = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    face_shape = Column(String)
    head_shape = Column(String)
    personal_color = Column(String)
    hair_condition = Column(String)
    scalp_condition = Column(String)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    memo = Column(String)
