from typing import Optional, Literal
from datetime import datetime

from pydantic import BaseModel


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
    is_active: Optional[bool] = True
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

class DesignerUpdate(BaseModel):
    user_name: Optional[str] = None
    user_phone_number: Optional[str] = None
    user_password: Optional[str] = None
    is_active: Optional[bool] = None
    memo: Optional[str] = None


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
    category_id: str
    category_name: str
    option_name: str
    image_source: Optional[str]
    is_user_option: bool = False  # True for user options, False for default options

    class Config:
        orm_mode = True

class CustomerDesignerMappingRead(BaseModel):
    id: int
    customer_id: str
    designer_id: str
    status: str
    requested_by: str
    requested_time: datetime
    responded_time: Optional[datetime] = None
    memo: Optional[str] = None

    class Config:
        from_attributes = True

class CustomerDesignerMappingCreate(BaseModel):
    customer_id: str
    memo: Optional[str] = None

class CustomerDesignerMappingUpdate(BaseModel):
    status: Literal["accepted", "rejected"]
    memo: Optional[str] = None

class DesignerRequestResponse(BaseModel):
    response: str  # 'accepted' or 'rejected'

class CustomerMeUpdate(BaseModel):
    user_name: Optional[str] = None
    user_phone_number: Optional[str] = None
    user_password: Optional[str] = None
