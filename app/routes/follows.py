from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.routes.auth import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.models.follow import Follow
from app.models.review import Review
from app.schemas.user import UserPublic
from app.schemas.review import ReviewPublic


router = APIRouter(prefix="/follows", tags=["follows"])

@router.post("/{user_id}", status_code=201)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail= "User cannot follow itself")

    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="Could not find user")
    
    follows = db.query(Follow).filter(Follow.follower_id==current_user.id, Follow.following_id==user_id).first()
    if follows:
        return {"following": True}
    db.add(Follow(follower_id=current_user.id, following_id=user_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # tratar o integrity error do unique constraint no model
        return {"following": True}
    return {"following": True}


@router.delete("/{user_id}", status_code=204)
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    follow = db.query(Follow).filter(Follow.follower_id==current_user.id, Follow.following_id==user_id).first()
    if not follow:
        return
    db.delete(follow)
    db.commit()
    return

@router.get("/me/following", response_model=list[UserPublic])
def list_following(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = db.execute(
        select(User).join(Follow, Follow.following_id==User.id).where(Follow.follower_id==current_user.id)
    ).scalars().all()
    return users

@router.get("/me/followers", response_model=list[UserPublic])
def list_followers(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = db.execute(
        select(User).join(Follow, Follow.follower_id==User.id).where(Follow.following_id==current_user.id)
    ).scalars().all()
    return users

@router.get("/me/feed", response_model=list[ReviewPublic])
def following_feed(current_user=Depends(get_current_user), 
                   db:Session=Depends(get_db), 
                   limit: int = Query(20, ge=1, le=100), 
                   offset: int = Query(0, ge=0),):
    
    qs = (
        db.query(Review)
        .options(joinedload(Review.book))
        .join(Follow, Follow.following_id == Review.user_id)
        .filter(Follow.follower_id == current_user.id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return qs

@router.get("/me/status/{user_id}")
def follow_status(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    exists = db.query(Follow).filter(Follow.follower_id==current_user.id, Follow.following_id==user_id).first()
    return {"following": bool(exists)}