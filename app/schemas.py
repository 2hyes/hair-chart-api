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
    name: str
    password: str
    phone_number: Optional[str]
    shop_number: str
    biz_number: str

class ShopRead(BaseModel):
    id: str
    name: str
    phone_number: str
    shop_number: str
    biz_number: str
    created_time: datetime

    class Config:
        orm_mode = True
