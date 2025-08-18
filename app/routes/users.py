from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.review import Review
from app.schemas.review import ReviewPublic
from app.dependencies import get_db
from app.schemas.user import UserPublic


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
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return qs

@router.get("/{user_id}", response_model=UserPublic)
def get_user_public(user_id: int, db: Session=Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.get("/{user_id}/reviews", response_model=list[ReviewPublic])
def get_user_reviews(user_id: int, db:Session = Depends(get_db), limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .filter(Review.user_id == user_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return qs