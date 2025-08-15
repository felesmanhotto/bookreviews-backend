from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.routes.auth import get_current_user
from app.models.review import Review
from app.schemas.review import ReviewPublic
from app.dependencies import get_db


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/reviews", response_model=list[ReviewPublic])
def my_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .filter(Review.user_id == current_user.id)
        .order_by(Review.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return qs