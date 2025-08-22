from pydantic import BaseModel, Field
from app.schemas.book import BookPublic
from typing import Optional

class ReviewCreate(BaseModel):
    book_id: str = Field(..., description="OpenLibrary work ID (e.g., OL82563W)")
    content: str
    rating: int = Field(..., ge=1, le=5)


class ReviewEdit(BaseModel):
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class ReviewPublic(BaseModel):
    id: int
    content: str
    rating: int
    user_id: int
    book: BookPublic

    class Config:
        from_attributes = True
