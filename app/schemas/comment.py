from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class CommentPublic(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime | None = None
    
    class Config:
        from_attributes = True

class CommentUser(BaseModel):
    id: int
    content: str
    user_id: int
    user_name: str
    created_at: datetime | None = None