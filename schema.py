from pydantic import BaseModel, Field, field_validator
from typing import Optional
from re import fullmatch
from uuid import UUID, uuid4

class BookItem(BaseModel):
    id: UUID
    title: str
    author: str
    category: str
    isbn: Optional[str] = None
    cover_art: Optional[str] = None
    
class BookCreate(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    title: str
    author: str
    category: str
    isbn: Optional[str] = None
    cover_art: Optional[str] = None
    
    @field_validator("category")
    def validate_category(cls, cat: str):
        if fullmatch(r"[A-Z]{3}[0-9]{6}", cat) is None:
            raise ValueError(f"Category must be formatted as [A-Z]{{3}}[0-9]{{6}}. Given: {cat:s}")
        return cat
