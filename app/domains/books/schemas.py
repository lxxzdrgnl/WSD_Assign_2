from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, Literal
from decimal import Decimal


class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255, example="The Great Gatsby")
    author: str = Field(min_length=1, max_length=100, example="F. Scott Fitzgerald")
    publisher: str = Field(min_length=1, max_length=100, example="Scribner")
    summary: Optional[str] = Field(None, max_length=500, example="A classic American novel")
    isbn: str = Field(min_length=10, max_length=20, pattern=r"^[0-9\-]+$", example="978-0743273565")
    price: Decimal = Field(gt=0, decimal_places=2, example=15.99)
    publication_date: date = Field(example="1925-04-10")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Great Gatsby",
                    "author": "F. Scott Fitzgerald",
                    "publisher": "Scribner",
                    "summary": "A classic American novel",
                    "isbn": "978-0743273565",
                    "price": 15.99,
                    "publication_date": "1925-04-10"
                }
            ]
        }
    }

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        cleaned = v.replace("-", "")
        if len(cleaned) not in [10, 13]:
            raise ValueError("ISBN must be 10 or 13 digits")
        if not cleaned.isdigit():
            raise ValueError("ISBN must contain only digits")
        return v


class BookUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, example="Updated Title")
    author: Optional[str] = Field(None, min_length=1, max_length=100, example="Updated Author")
    publisher: Optional[str] = Field(None, min_length=1, max_length=100, example="Updated Publisher")
    summary: Optional[str] = Field(None, max_length=500, example="Updated summary")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2, example=19.99)
    publication_date: Optional[date] = Field(None, example="2024-01-01")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Title",
                    "price": 19.99
                }
            ]
        }
    }


class BookResponse(BaseModel):
    id: int
    seller_id: int
    title: str
    author: str
    publisher: str
    summary: Optional[str]
    isbn: str
    price: Decimal
    publication_date: date
    created_at: datetime
    updated_at: datetime
    view_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    content: list[BookResponse]
    page: int
    size: int
    total_elements: int
    total_pages: int
    sort: str


class BookSearchParams(BaseModel):
    keyword: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    sort: Literal["title", "author", "price", "publication_date", "created_at", "view_count"] = "created_at"
    order: Literal["asc", "desc"] = "desc"
