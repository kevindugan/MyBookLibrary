from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CategoriesTB(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(String(9), nullable=False)
    cat_path = Column(String, nullable=False)
