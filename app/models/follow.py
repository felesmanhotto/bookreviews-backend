from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime, func, CheckConstraint
from app.db.database import Base

class Follow(Base):
    __tablename__= "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow_pair"),
        CheckConstraint("follower_id <> following_id", name="ck_no_self_follow"),
        )