from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    password: Optional[str]

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]

    class Config:
        orm_mode = True
