from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Text, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_1_5"),
        UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
    )

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    comments = relationship("Comment", back_populates="review", cascade="all, delete-orphan")
    likes = relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")
