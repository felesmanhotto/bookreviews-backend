from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)  # external id (openlibrary_id)
    title = Column(String, nullable=False, index=True)
    author = Column(String, index=True, nullable=True)
    cover_url = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
