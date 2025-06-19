from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users" # user_type: customer, shop, designer
    
    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), unique=True, nullable=False)
    user_type = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    

class Shop(Base):
    __tablename__ = "shops"

    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    number = Column(String(20), nullable=False)
    biz_number = Column(String(20), nullable=False)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)


class Designer(Base):
    __tablename__ = "designers"

    seq = Column(Integer, primary_key=True, index=True)
    id = Column(String(50), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    belonging_shop_id = Column(String(50), ForeignKey("shops.id"), unique=True, nullable=False)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    memo = Column(String(4000), nullable=True)


# class UserHairProfile(Base):
#     __tablename__ = "user_hair_profile"

#     seq = Column(Integer, primary_key=True, index=True)
#     user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
#     face_shape = Column(String)
#     head_shape = Column(String)
#     personal_color = Column(String)
#     hair_condition = Column(String)
#     scalp_condition = Column(String)
#     created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
#     updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
#     memo = Column(String)
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey
from .database import Base

class ChartItemUserOption(Base):
    __tablename__ = "chart_item_user_options"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(50), nullable=False)
    category_name = Column(String(50), nullable=False)
    option_name = Column(String(100), unique=True, nullable=False)
    image_source = Column(String(500), nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    updated_time = Column(TIMESTAMP(timezone=False), server_default=text("CURRENT_TIMESTAMP(0)"), nullable=False)
    