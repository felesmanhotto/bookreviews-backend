from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.comment import Comment
from app.models.review import Review
from app.schemas.comment import CommentCreate, CommentPublic
from app.routes.auth import get_current_user
from app.dependencies import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/review/{review_id}", response_model=CommentPublic, status_code=201)
def create_comment(review_id: int, payload: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rev = db.get(Review, review_id)
    if not rev:
        raise HTTPException(404, "Review não encontrada")

    c = Comment(review_id=review_id, user_id=current_user.id, content=payload.content)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/review/{review_id}", response_model=list[CommentPublic])
def list_comments(review_id: int, db: Session=Depends(get_db), limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0),):
    qs = (db.query(Comment)
          .filter(Comment.review_id == review_id)
          .order_by(Comment.created_at.desc())
          .limit(limit)
          .offset(offset)
          .all())
    
    return qs