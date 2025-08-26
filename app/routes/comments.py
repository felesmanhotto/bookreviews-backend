from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.comment import Comment
from app.models.review import Review
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentPublic, CommentUser
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

@router.get("/review/{review_id}", response_model=list[CommentUser])
def list_comments(review_id: int, db: Session=Depends(get_db), limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0),):
    if not db.get(Review, review_id):
        raise HTTPException(404, "Review not found")
    
    stmt = (
        select(
            Comment.id,
            Comment.content,
            Comment.user_id,
            User.name.label("user_name"),
            Comment.created_at,
        )
        .join(User, User.id == Comment.user_id)
        .where(Comment.review_id == review_id)
        .order_by(Comment.id.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()
    # converter row tuples -> dicts compatíveis com CommentWithUser
    return [
        {
            "id": row.id,
            "content": row.content,
            "user_id": row.user_id,
            "user_name": row.user_name,
            "created_at": row.created_at,
        }
        for row in rows
    ]

@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session=Depends(get_db), current_user=Depends(get_current_user)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(403, "You cannot delete this comment")
    
    db.delete(comment)
    db.commit()
    return