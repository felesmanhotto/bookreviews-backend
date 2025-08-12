from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UserPublic(BaseModel):
    id: int
    nome: str
    email: EmailStr
    class Config:
        from_attributes = True  # pydantic permite retornar ORM

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"