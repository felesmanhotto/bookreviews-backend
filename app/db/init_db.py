from app.db.database import Base, engine
from app.models.user import User
from app.models.book import Book
from app.models.review import Review
from app.models.comment import Comment
from app.models.review_like import ReviewLike


def init_db():
    print("Conectando ao banco...")
    print(engine.url)  
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
