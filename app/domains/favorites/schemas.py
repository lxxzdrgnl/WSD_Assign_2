"""
Favorites Schemas
위시리스트 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FavoriteAddRequest(BaseModel):
    """위시리스트 추가 요청"""
    book_id: int = Field(..., gt=0, description="도서 ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "book_id": 1
            }
        }
    }


class FavoriteResponse(BaseModel):
    """위시리스트 응답"""
    id: int = Field(..., description="위시리스트 ID")
    user_id: int = Field(..., description="사용자 ID")
    book_id: int = Field(..., description="도서 ID")
    book_title: str = Field(..., description="도서 제목")
    book_author: str = Field(..., description="저자")
    book_price: int = Field(..., description="가격")
    book_thumbnail: Optional[str] = Field(None, description="썸네일 URL")
    created_at: datetime = Field(..., description="추가일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 11,
                "book_id": 1,
                "book_title": "채식주의자",
                "book_author": "한강",
                "book_price": 10800,
                "book_thumbnail": None,
                "created_at": "2025-12-06T12:00:00"
            }
        }
    }


class FavoriteListResponse(BaseModel):
    """위시리스트 목록 응답"""
    content: list[FavoriteResponse] = Field(..., description="위시리스트 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., alias="totalElements", description="전체 개수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 20,
                "total_elements": 5,
                "total_pages": 1
            }
        }
    }
