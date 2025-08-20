from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import httpx
from app.db.database import SessionLocal
from app.models.book import Book
from app.schemas.book import BookPublic
from app.dependencies import get_db

router = APIRouter(prefix="/books", tags=["books"])

OPENLIBRARY_SEARCH = "https://openlibrary.org/search.json"
OPENLIBRARY_WORK = "https://openlibrary.org/works/{olid}.json"
OPENLIBRARY_COVER = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

@router.get("/search", response_model=list[BookPublic])
async def search_books(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    # Busca na OpenLibrary (simplificada). Vamos retornar e também preparar cache básico.
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(OPENLIBRARY_SEARCH, params={"q": q, "limit": 12})
        r.raise_for_status()
        data = r.json()

    results: list[BookPublic] = []
    for doc in data.get("docs", [])[:12]:
        work_key = doc.get("key")  # ex: "/works/OL82563W"
        if not work_key or not work_key.startswith("/works/"):
            continue
        olid = work_key.split("/")[-1]
        title = doc.get("title") or "Sem título"
        authors = "; ".join(doc.get("author_name", [])[:3]) if doc.get("author_name") else None
        cover_url = None
        if doc.get("cover_i"):
            cover_url = OPENLIBRARY_COVER.format(cover_id=doc["cover_i"])

        # upsert simples no cache
        bk = db.get(Book, olid)
        if not bk:
            bk = Book(id=olid, title=title, author=authors, cover_url=cover_url)
            db.add(bk)
        else:
            bk.title = title
            bk.author = authors
            bk.cover_url = cover_url
        results.append(BookPublic.model_validate(bk))

    db.commit()
    return results

@router.get("/{olid}", response_model=BookPublic)
async def get_book(olid: str, db: Session = Depends(get_db)):
    # tenta cache local primeiro
    bk = db.get(Book, olid)
    if bk:
        return bk

    # busca details do work
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(OPENLIBRARY_WORK.format(olid=olid))
        if r.status_code == 404:
            raise HTTPException(404, "Livro não encontrado na OpenLibrary")
        r.raise_for_status()
        data = r.json()

    title = data.get("title") or "Sem título"
    authors = None
    if "authors" in data:
        names = []
        for a in data["authors"]:
            # a pode ter {"author": {"key": "/authors/OL...A"}}
            # sem mais uma chamada, não temos nomes; então ficamos no cache básico
            pass
        # como fallback, mantenha None; nomes já vêm melhor pelo endpoint /search.
    bk = Book(id=olid, title=title, author=authors, cover_url=None)
    db.add(bk)
    db.commit()
    db.refresh(bk)
    return bk
