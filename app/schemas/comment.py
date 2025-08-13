from pydantic import BaseModel

class CommentCreate(BaseModel):
    content: str

class CommentPublic(BaseModel):
    id: int
    content: str
    user_id: int

    class Config:
        from_attributes = True
