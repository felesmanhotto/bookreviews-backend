from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    name: str
    created_at: datetime
    bio: str | None = None
    class Config:
        from_attributes = True  # pydantic permite retornar ORM

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"