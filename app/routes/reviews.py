from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.models.book import Book
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewPublic
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


@router.get("/book/{olid}", response_model=list[ReviewPublic])
def list_reviews_by_book(olid: str, db: Session = Depends(get_db)):
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .filter(Review.book_id == olid)
        .order_by(Review.id.desc())
        .limit(10)
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