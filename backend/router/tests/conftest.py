import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def db_session(postgresql):
    from sqlalchemy import URL, create_engine
    from sqlalchemy.orm import sessionmaker
    from ...models import Base

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

class Helpers:
    @staticmethod
    def get_client(session) -> TestClient:
        from ...backendManager import api
        from ...database import get_db
        api.dependency_overrides[get_db] = lambda: session
        return TestClient(app=api)
    
@pytest.fixture
def helpers():
    return Helpers