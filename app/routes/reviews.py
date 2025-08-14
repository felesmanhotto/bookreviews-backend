from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.models.book import Book
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewPublic
from app.routes.auth import get_current_user 
from app.dependencies import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewPublic, status_code=201)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    book = db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not in cache. Run /books/search first")

    review = Review(
        user_id=current_user.id,
        book_id=book.id,
        content=payload.content,
        rating=payload.rating,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/book/{olid}", response_model=list[ReviewPublic])
def list_reviews_by_book(olid: str, db: Session = Depends(get_db)):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .filter(Review.book_id == olid)
        .order_by(Review.id.desc())
        .all()
    )
    return qs


@router.get("/feed", response_model=list[ReviewPublic])
def recent_reviews(db: Session = Depends(get_db)):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .order_by(Review.created_at.desc())
        .limit(20)
        .all()
    )
    return qs