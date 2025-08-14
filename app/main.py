from fastapi import FastAPI
from app.routes import auth, books, reviews, comments

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(reviews.router)
app.include_router(comments.router)
