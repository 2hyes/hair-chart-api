from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerCreate(BaseModel):
    id: str
    user_name: str
    user_password: str
    user_phone_number: str

class CustomerRead(BaseModel):
    id: str
    user_name: str
    user_phone_number: str

    class Config:
        orm_mode = True


class ShopCreate(BaseModel):
    id: str
    user_name: str
    user_password: str
    user_phone_number: str

    shop_name: str
    shop_number: str
    shop_biz_number: str

class ShopRead(BaseModel):
    id: str
    user_name: str
    user_phone_number: str

    shop_name: str
    shop_number: str
    shop_biz_number: str

    class Config:
        orm_mode = True


class DesignerCreate(BaseModel):
    id: str
    user_name: str
    user_password: str
    user_phone_number: str
    
    belonging_shop_id: Optional[str] = None
    memo:  Optional[str] = None

class DesignerCreateResponse(BaseModel):
    id: str
    user_name: str
    user_phone_number: str

    # designer info
    belonging_shop_id: Optional[str] = None
    is_active: bool
    memo:  Optional[str] = None

    class Config:
        orm_mode = True

class DesignerRead(BaseModel):
    id: str
    user_name: str
    user_phone_number: str

    # designer info
    belonging_shop_id: str
    # customer_count: int
    # recent_chart_created_time: datetime
    is_active: bool
    created_time: datetime
    memo: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    id: str
    password: str
    user_type: str

# class UserHairProfileCreate(BaseModel):
#     user_id: str
#     face_shape: Optional[str]
#     head_shape: Optional[str]
#     personal_color: Optional[str]
#     hair_condition: Optional[str]
#     scalp_condition: Optional[str]
#     memo: Optional[str] = Field(default="")

# class UserHairProfileRead(BaseModel):
#     seq: int
#     user_id: str
#     face_shape: Optional[str]
#     head_shape: Optional[str]
#     personal_color: Optional[str]
#     hair_condition: Optional[str]
#     scalp_condition: Optional[str]
#     created_time: datetime
#     updated_time: datetime
#     memo: Optional[str] = Field(default="")

#     class Config:
#         orm_mode = True

class ChartItemUserOption(BaseModel):
    user_id: str
    category_id: str
    category_name: str
    option_name: str
    image_source: Optional[str] = None

    class Config:
        orm_mode = True

class ChartItemUserOptionRead(BaseModel):
    id: str
    user_id: str
    category_id: str
    category_name: str
    option_name: str
    image_source: Optional[str] = None
    created_time: datetime
    updated_time: datetime

    class Config:
        orm_mode = True

class ChartItemDefaultOption(BaseModel):
    category_id: str
    category_name: str
    option_name: str
    image_source: Optional[str]

    class Config:
        orm_mode = True

class ChartItemOptionMerged(BaseModel):
    user_id: Optional[str]
    category_id: str
    category_name: str
    option_name: str
    image_source: Optional[str]
    is_user_option: bool = False  # True for user options, False for default options

    class Config:
        orm_mode = True
