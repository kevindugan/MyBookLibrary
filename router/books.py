from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy import select, exc
from sqlalchemy.orm import Session

from models import BooksTB, CategoriesTB

router = APIRouter(tags=["books"], prefix="/api/v1/books")

@router.get("/list")
async def list_books(limit: int = None, db: Session = Depends(get_db)) -> dict:
    labels = ["unique_id", "title", "author", "category", "cover"]
    sql_query = (
        select(
            BooksTB.id,
            BooksTB.title,
            BooksTB.author,
            CategoriesTB.cat_path,
            BooksTB.cover_art
        )
        .join(CategoriesTB, CategoriesTB.id == BooksTB.category)
    )
    
    try:
        list_results = [dict(zip(labels,it)) for it in db.execute(sql_query).all()]
    except exc.OperationalError as e:
        raise HTTPException(status_code=400, detail="unknown error")
    
    return {"result": [
        {
            key: val if key != "category" else val.replace("|", " / ") 
            for key,val in it.items()
        } for it in list_results[:limit]
    ]}

@router.get("/list-by-category")
async def list_books_category(limit: int = None, db: Session = Depends(get_db)) -> dict:
    labels = ["unique_id", "title", "author", "cover", "category"]
    sql_query = (
        select(
            BooksTB.id,
            BooksTB.title,
            BooksTB.author,
            BooksTB.cover_art,
            CategoriesTB.cat_path
        )
        .join(CategoriesTB, CategoriesTB.id == BooksTB.category)
        .order_by(CategoriesTB.id, BooksTB.author, BooksTB.title)
    )
    
    try:
        list_results = [dict(zip(labels,it)) for it in db.execute(sql_query).all()]
    except exc.OperationalError as e:
        raise HTTPException(status_code=400, detail="unknown error")
    
    return {"result": [
        {
            key: val if key != "category" else val.replace("|", " / ") 
            for key,val in it.items()
        } for it in list_results[:limit]
    ]}
