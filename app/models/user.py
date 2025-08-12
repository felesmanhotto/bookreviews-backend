from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
