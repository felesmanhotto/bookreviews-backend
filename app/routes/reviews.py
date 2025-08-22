from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.models.book import Book
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewPublic, ReviewEdit
from app.routes.auth import get_current_user 
from app.dependencies import get_db
import httpx

router = APIRouter(prefix="/reviews", tags=["reviews"])

OPENLIBRARY_WORK = "https://openlibrary.org/works/{olid}.json"
OPENLIBRARY_COVER = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"


async def ensure_book_cached(db: Session, olid: str):
    bk = db.get(Book, olid)
    if bk:
        return bk

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(OPENLIBRARY_WORK.format(olid=olid))
        if r.status_code == 404:
            raise HTTPException(status_code=400, detail="Book not found on OpenLibrary")
        r.raise_for_status()
        data = r.json()

    title = data.get("title") or "Untitled"
    # authors list in /works requires extra calls to resolve names; we keep None here.
    cover_url = None
    covers = data.get("covers")
    if isinstance(covers, list) and len(covers) > 0:
        cover_url = OPENLIBRARY_COVER.format(cover_id=covers[0])

    bk = Book(id=olid, title=title, authors=None, cover_url=cover_url)
    db.add(bk)
    db.commit()
    db.refresh(bk)
    return bk


@router.post("", response_model=ReviewPublic, status_code=201)
async def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    book = db.get(Book, payload.book_id)
    if not book:
        book = await ensure_book_cached(db, payload.book_id)

    existing = (
    db.query(Review)
    .filter(Review.user_id == current_user.id, Review.book_id == book.id)
    .first()
)
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this book")

    review = Review(
        user_id=current_user.id,
        book_id=book.id,
        content=payload.content,
        rating=payload.rating,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    db.refresh(book)    # eager attach for response
    review.book = book
    return review


@router.put("/{review_id}", response_model=ReviewPublic)
def edit_review(review_id: int, payload: ReviewEdit, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rev = db.query(Review).options(joinedload(Review.book)).filter(Review.id == review_id).first()
    if not rev:
        raise HTTPException(status_code=400, detail="Review not found")
    if rev.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    rev.content = payload.content if payload.content is not None else rev.content
    rev.rating = payload.rating if payload.rating is not None else rev.rating

    db.commit()
    db.refresh(rev)
    return rev


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rev = db.get(Review, review_id)
    if not rev:
        raise HTTPException(status_code=400, detail="Review not found")
    if rev.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    db.delete(rev)
    db.commit()

    return

@router.get("/book/{olid}", response_model=list[ReviewPublic])
def list_reviews_by_book(olid: str, db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .filter(Review.book_id == olid)
        .order_by(Review.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return qs


@router.get("/feed", response_model=list[ReviewPublic])
def recent_reviews(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return qs