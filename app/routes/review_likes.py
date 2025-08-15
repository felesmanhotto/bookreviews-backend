from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.review import Review
from app.models.review_like import ReviewLike
from app.routes.auth import get_current_user
from app.dependencies import get_db

router = APIRouter(prefix="/reviews", tags=["review-likes"])

@router.post("/review/{review_id}", status_code=201)
def like_review(review_id: int, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    rev = db.get(Review, review_id)
    if not rev:
     raise HTTPException(404, "Review não encontrada")
    
    existing = (
        db.query(ReviewLike)
        .filter(ReviewLike.review_id == review_id, ReviewLike.user_id == current_user.id)
        .first()
    )

    if existing:    # toggle
        db.delete(existing)
        db.commit()
        return {"liked": False}
    
    like = ReviewLike(review_id=review_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return {"liked": True}


@router.get("/{review_id}/likes/count")
def count_likes(review_id: int, db: Session = Depends(get_db)):
    count = db.query(func.count(ReviewLike.id)).filter(ReviewLike.review_id == review_id).scalar()
    return {"review_id": review_id, "likes": count or 0}