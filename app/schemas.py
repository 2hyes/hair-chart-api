from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    id: str
    name: str
    password: str
    phone_number: Optional[str]
    memo: Optional[str]

class UserRead(BaseModel):
    seq: int
    id: str
    name: str
    phone_number: Optional[str]
    created_time: datetime
    updated_time: datetime
    memo: Optional[str]

    class Config:
        orm_mode = True
