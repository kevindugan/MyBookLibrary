import pytest
from models import CategoriesTB
from fastapi.testclient import TestClient

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
    
def test_search_categories(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="ANT000000", cat_path="Antiques & Collectibles|General"),
        CategoriesTB(cat_id="ANT001000", cat_path="Antiques & Collectibles|Americana"),
        CategoriesTB(cat_id="ARC005030", cat_path="Architecture|History|Medieval"),
        CategoriesTB(cat_id="FIC027150", cat_path="Fiction|Romance|History|Medieval"),
        CategoriesTB(cat_id="FIC027170", cat_path="Fiction|Romance|History|Victorian"),
        CategoriesTB(cat_id="HIS002020", cat_path="History|Ancient|Rome"),
        CategoriesTB(cat_id="SCI051000", cat_path="Science|Physics|Nuclear"),
        CategoriesTB(cat_id="SCI034000", cat_path="Science|History"),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # Get query endpoint
    response = client.get("/api/v1/categories/search?query=his")
    assert response.status_code == 200
    assert response.json() == {
        "result": [
            {"id": "SCI034000", "name": "Science / History"},
            {"id": "ARC005030", "name": "Architecture / History / Medieval"},
            {"id": "FIC027150", "name": "Fiction / Romance / History / Medieval"},
            {"id": "FIC027170", "name": "Fiction / Romance / History / Victorian"},
            {"id": "HIS002020", "name": "History / Ancient / Rome"},
        ]
    }
    
def test_search_categories_limit_2(db_session):
    db_session.add_all([
        CategoriesTB(cat_id="ANT000000", cat_path="Antiques & Collectibles|General"),
        CategoriesTB(cat_id="ANT001000", cat_path="Antiques & Collectibles|Americana"),
        CategoriesTB(cat_id="ARC005030", cat_path="Architecture|History|Medieval"),
        CategoriesTB(cat_id="FIC027150", cat_path="Fiction|Romance|History|Medieval"),
        CategoriesTB(cat_id="FIC027170", cat_path="Fiction|Romance|History|Victorian"),
        CategoriesTB(cat_id="HIS002020", cat_path="History|Ancient|Rome"),
        CategoriesTB(cat_id="SCI051000", cat_path="Science|Physics|Nuclear"),
        CategoriesTB(cat_id="SCI034000", cat_path="Science|History"),
    ])
    db_session.commit()
    
    client = get_client(db_session)
    
    # Get query endpoint
    response = client.get("/api/v1/categories/search?query=his&limit=2")
    assert response.status_code == 200
    assert len(response.json()["result"]) == 2
    assert response.json() == {
        "result": [
            {"id": "SCI034000", "name": "Science / History"},
            {"id": "ARC005030", "name": "Architecture / History / Medieval"},
        ]
    }
