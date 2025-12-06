"""
Library Schemas
구매한 도서 관련 응답 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LibraryBookResponse(BaseModel):
    """구매한 도서 응답"""
    book_id: int = Field(..., description="도서 ID")
    title: str = Field(..., description="도서 제목")
    author: str = Field(..., description="저자")
    publisher: str = Field(..., description="출판사")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    purchased_at: datetime = Field(..., description="구매일")
    order_id: int = Field(..., description="주문 ID")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "book_id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "publisher": "Scribner",
                "thumbnail_url": "https://example.com/thumbnail.jpg",
                "purchased_at": "2025-12-01T10:00:00",
                "order_id": 5
            }
        }
    }


class LibraryListResponse(BaseModel):
    """구매한 도서 목록 응답"""
    content: list[LibraryBookResponse] = Field(..., description="구매한 도서 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., description="전체 도서 수")
    total_pages: int = Field(..., description="전체 페이지 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 20,
                "total_elements": 10,
                "total_pages": 1
            }
        }
    }
