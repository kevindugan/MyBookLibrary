from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey, Uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CategoriesTB(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(String(9), nullable=False, unique=True)
    cat_path = Column(String, nullable=False, unique=True)
    
class BooksTB(Base):
    __tablename__ = "books"
    id = Column(Uuid, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(VARCHAR, nullable=True)
    cover_art = Column(VARCHAR, nullable=True)
    category = Column("category", Integer, ForeignKey("categories.id"))
