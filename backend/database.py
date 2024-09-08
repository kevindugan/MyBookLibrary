from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from .config import config

def get_db():
    url = URL.create(
        "postgresql",
        username=config["DB_USER"],
        password=config["DB_PASS"],
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        port=config["DB_PORT"]
    )
    engine = create_engine(url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
