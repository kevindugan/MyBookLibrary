import pytest
from fastapi.testclient import TestClient
from models import BooksTB, CategoriesTB
from uuid import uuid3, NAMESPACE_OID

@pytest.fixture
def db_session(postgresql):
    from sqlalchemy import URL, create_engine
    from sqlalchemy.orm import sessionmaker
    from models import Base

    url = URL.create(
        "postgresql",
        username=postgresql.info.user,
        password=postgresql.info.password,
        host=postgresql.info.host,
        port=postgresql.info.port,
        database=postgresql.info.dbname
    )
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = localSession()
    yield db
    db.close()
    
def get_client(session) -> TestClient:
    from booksApp import api
    from database import get_db
    api.dependency_overrides[get_db] = lambda: session
    return TestClient(app=api)

def test_list_books_all(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2]),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # List all endpoint
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"cover": None, "unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category"},
            {"cover": None, "unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category"},
            {"cover": None, "unique_id": str(id_list[2]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category"}
        ]
    }
    
def test_list_books_limit(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2]),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # List all endpoint
    response = client.get("/api/v1/books/list?limit=2")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"cover": None, "unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category"},
            {"cover": None, "unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category"},
        ]
    }

def test_list_books_with_cover(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(3)]
    db_session.add_all([
        BooksTB(title="Book 1", author="Someone", category="1", id=id_list[0]),
        BooksTB(title="Book 2", author="Someone", category="2", id=id_list[1], cover_art="data:image/jpg;base64,/9j/4AAQSkZJRgABAQ"),
        BooksTB(title="Other Book", author="Someone Else", category="2", id=id_list[2], cover_art="data:image/jpg;base64,/9j/4AAQSjZJqgABAQ"),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # List all, some have cover
    response = client.get("/api/v1/books/list")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"cover": None, "unique_id": str(id_list[0]), "title": "Book 1", "author": "Someone", "category": "Category / Sub Category"},
            {"cover": "data:image/jpg;base64,/9j/4AAQSkZJRgABAQ", "unique_id": str(id_list[1]), "title": "Book 2", "author": "Someone", "category": "Category / Other Sub Category"},
            {"cover": "data:image/jpg;base64,/9j/4AAQSjZJqgABAQ", "unique_id": str(id_list[2]), "title": "Other Book", "author": "Someone Else", "category": "Category / Other Sub Category"}
        ]
    }
    
def test_list_books_by_category(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="CAT001000", cat_path="Category|Sub Category"),
        CategoriesTB(cat_id="CAT002000", cat_path="Category|Other Sub Category"),
    ])
    db_session.commit()
    id_list = [uuid3(NAMESPACE_OID, f"test {it}") for it in range(4)]
    db_session.add_all([
        BooksTB(title="Other Book", author="New Someone", category="2", id=id_list[0]),
        BooksTB(title="Book 1", author="Someone", category="2", id=id_list[1]),
        BooksTB(title="Book 2", author="Someone", category="1", id=id_list[2]),
        BooksTB(title="A Book 2", author="Someone", category="1", id=id_list[3]),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # List all books, ordered by category,author,title
    response = client.get("/api/v1/books/list-by-category")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"unique_id": str(id_list[3]), "title": "A Book 2", "author": "Someone", "category": "Category / Sub Category", "cover": None},
            {"unique_id": str(id_list[2]), "title": "Book 2", "author": "Someone", "category": "Category / Sub Category", "cover": None},
            {"unique_id": str(id_list[0]), "title": "Other Book", "author": "New Someone", "category": "Category / Other Sub Category", "cover": None},
            {"unique_id": str(id_list[1]), "title": "Book 1", "author": "Someone", "category": "Category / Other Sub Category", "cover": None},
        ]
    }