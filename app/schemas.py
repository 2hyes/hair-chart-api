from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerCreate(BaseModel):
    id: str
    name: str
    password: str
    phone_number: Optional[str]
    memo: Optional[str]

class CustomerRead(BaseModel):
    id: str
    name: str
    phone_number: Optional[str]
    memo: Optional[str]

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
