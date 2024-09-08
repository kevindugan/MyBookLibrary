from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy import select, or_, exc
from sqlalchemy.orm import Session
from re import compile
from urllib.parse import unquote

from models import CategoriesTB

router = APIRouter(tags=["categories"], prefix="/api/v1/categories")

@router.get("/search")
async def search(query: str, limit: int = 10, db: Session = Depends(get_db)) -> dict:
    query_list = [it.strip() for it in unquote(query).split(" ") if it.strip() not in ["&"]]
    query_terms = [
        CategoriesTB.cat_path.ilike(it)
            for word in query_list
            for it in [f"{word}%" ,f"% {word}%", f"%|{word}%"]
    ]
    labels = ["id", "name"]
    sql_query = (
        select(
            CategoriesTB.cat_id,
            CategoriesTB.cat_path)
        .where(or_(*query_terms))
    )
    
    try:
        search_results = [dict(zip(labels,it)) for it in db.execute(sql_query).all()]
    except exc.OperationalError as e:
        raise HTTPException(status_code=400, detail="unknown error")

    # Sort based on how far from leaf the hit is.
    pattern = compile("|".join(f"^{word.lower()}|[| ]{word.lower()}" for word in query_list))
    def rank(key: str):
        return sum(2**idx / (len(pattern.findall(it.lower()))+1)**-idx for idx,it in enumerate(reversed(key.split('|'))))
    hits: list[tuple[float,dict]] = sorted([(rank(it["name"]), it) for it in search_results], key=lambda x: (x[0], x[1]["name"]))
    # print([(it,jt["name"]) for it,jt in hits[:limit]])

    return {"result": [
        {
            key: val if key != "name" else val.replace("|", " / ")
            for key,val in it[1].items()
        } for it in hits[:limit]
    ]}
    
