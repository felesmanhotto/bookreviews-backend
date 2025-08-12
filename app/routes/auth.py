from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import get_settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# dependência para obter sessão do DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=UserPublic, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    new_user = User(nome=user.nome, email=user.email, senha_hash=hash_password(user.senha))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm espera fields username e password
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user( token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    cred_exc = HTTPException(status_code=401, detail="Token inválido ou expirado")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.get(User, int(user_id))
    if not user:
        raise cred_exc
    return user


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user