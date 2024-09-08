from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, exc
from sqlalchemy.orm import Session
from uuid import uuid4

from ..models import BooksTB, CategoriesTB
from ..schema import BookItem, BookCreate
from ..database import get_db

router = APIRouter(tags=["books"], prefix="/api/v1/books")

@router.get("/list")
async def list_books(limit: int = None, db: Session = Depends(get_db)) -> dict:
    labels = ["unique_id", "title", "author", "category", "cover_art", "isbn"]
    sql_query = (
        select(
            BooksTB.id,
            BooksTB.title,
            BooksTB.author,
            CategoriesTB.cat_path,
            BooksTB.cover_art,
            BooksTB.isbn
        )
        .join(CategoriesTB, CategoriesTB.id == BooksTB.category)
    )
    sql_query_2 = (
        select(
            BooksTB.id,
            BooksTB.title,
            BooksTB.author,
            BooksTB.category,
            BooksTB.cover_art,
            BooksTB.isbn
        )
        .where(BooksTB.category == None)
    )
    
    try:
        list_results = [dict(zip(labels,it)) for it in db.execute(sql_query).all()] + \
                       [dict(zip(labels,it)) for it in db.execute(sql_query_2).all()]
    except exc.OperationalError as e:
        raise HTTPException(status_code=400, detail="unknown error")
    
    return {"result": [
        {
            key: val if key != "category" else (val.replace("|", " / ") if val is not None else None)
            for key,val in it.items()
        } for it in list_results[:limit]
    ]}

@router.get("/list-by-category")
async def list_books_category(limit: int = None, db: Session = Depends(get_db)) -> dict:
    labels = ["unique_id", "title", "author", "cover_art", "category", "isbn"]
    sql_query = (
        select(
            BooksTB.id,
            BooksTB.title,
            BooksTB.author,
            BooksTB.cover_art,
            CategoriesTB.cat_path,
            BooksTB.isbn
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
    
@router.post("/add")
async def add_book(data: BookCreate, db: Session = Depends(get_db)) -> BookItem:
    # Recover category id
    sql_query = (
        select(CategoriesTB.id)
        .where(CategoriesTB.cat_id == data.category)
    )
    cat_id = db.execute(sql_query).mappings().one_or_none().id
    db_model = {**data.model_dump(), **{"category": cat_id}}
    db.add(BooksTB(**db_model))
    db.commit()
    
    
    
    # cat_id = db.execute(sql_query).first()[0]
    # model_dict = data.model_dump()
    # model_dict["category"] = cat_id
    # model_dict["id"] = uuid4()
    # db.add(BooksTB(**model_dict))
    # db.commit()
    # return data
    return BookItem(**data.model_dump())



    # sql_query = (
    #     select(CategoriesTB.id)
    #     .filter(CategoriesTB.cat_id == data.category)
    # )
    # query = db.execute(sql_query).first()
    # newBook = BooksTB(
    #     title=data.title,
    #     author=data.author,
    #     isbn=data.isbn,
    #     cover_art=data.cover,
    #     category=query[0][0]
    # )
    # db.add(newBook)
    # db.commit()
    # return data
