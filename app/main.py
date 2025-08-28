from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, books, reviews, comments, users, review_likes, follows

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(reviews.router)
app.include_router(comments.router)
app.include_router(users.router)
app.include_router(review_likes.router)
app.include_router(follows.router)