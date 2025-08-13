from pydantic import BaseModel

class BookBase(BaseModel):
    id: str
    title: str
    author: str | None = None
    cover_url: str | None = None

class BookPublic(BookBase):
    class Config:
        from_attributes = True
