from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        from_attributes = True  # pydantic permite retornar ORM

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"