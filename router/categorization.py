from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy import select, or_, exc
from sqlalchemy.orm import Session
from re import compile

from models import CategoriesTB

router = APIRouter(tags=["categories"], prefix="/api/v1/categories")

@router.get("/search")
async def search(query: str, limit: int = 10, db: Session = Depends(get_db)) -> dict:    
    sql_query = (
        select(
            CategoriesTB.cat_id,
            CategoriesTB.cat_path)
        .where(or_(
            CategoriesTB.cat_path.ilike(f"{query}%"),
            CategoriesTB.cat_path.ilike(f"% {query}%"),
            CategoriesTB.cat_path.ilike(f"%|{query}%")
        ))
    )
    
    try:
        search_results = [it[1] for it in db.execute(sql_query).all()]
    except exc.OperationalError as e:
        raise HTTPException(status_code=400, detail="unknown error")

    # Sort based on how far from leaf the hit is.
    pattern = compile(f"^{query.lower()}|[| ]{query.lower()}")
    def rank(key: str):
        return sum(2**idx * int(pattern.search(it.lower()) is not None) for idx,it in enumerate(reversed(key.split('|'))))
    hits: list[tuple[float,str]] = sorted([(rank(it), it) for it in search_results])

    return {"result": [it[1].replace("|", " / ") for it in hits[:limit]]}
    
