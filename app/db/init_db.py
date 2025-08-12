from app.db.database import Base, engine
from app.models.user import User

def init_db():
    print("Conectando ao banco...")
    print(engine.url)  
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
