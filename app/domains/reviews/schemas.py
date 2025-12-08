"""
Reviews Schemas
리뷰 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class ReviewCreateRequest(BaseModel):
    """리뷰 작성 요청"""
    book_id: int = Field(..., gt=0, description="도서 ID")
    rating: int = Field(..., ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, min_length=10, max_length=2000, description="리뷰 내용 (10-2000자)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "book_id": 1,
                "rating": 5,
                "content": "정말 감동적인 소설입니다. 주인공의 성장 과정이 인상 깊었어요."
            }
        }
    }


class ReviewUpdateRequest(BaseModel):
    """리뷰 수정 요청"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="평점 (1-5)")
    content: Optional[str] = Field(None, min_length=10, max_length=2000, description="리뷰 내용")

    model_config = {
        "json_schema_extra": {
            "example": {
                "rating": 4,
                "content": "다시 읽어보니 4점이 적당한 것 같습니다. 여전히 좋은 작품이에요."
            }
        }
    }


class ReviewResponse(BaseModel):
    """리뷰 응답"""
    id: int = Field(..., description="리뷰 ID")
    book_id: int = Field(..., description="도서 ID")
    user_id: int = Field(..., description="작성자 ID")
    user_name: str = Field(..., description="작성자 이름")
    rating: int = Field(..., description="평점")
    content: Optional[str] = Field(None, description="리뷰 내용", alias="content")
    like_count: int = Field(0, description="좋아요 수")
    is_liked: bool = Field(False, description="현재 사용자의 좋아요 여부")
    created_at: datetime = Field(..., description="작성일")
    updated_at: datetime = Field(..., description="수정일")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "populate_by_alias": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "book_id": 1,
                "user_id": 2,
                "user_name": "김서점",
                "rating": 5,
                "content": "정말 감동적인 소설입니다.",
                "like_count": 15,
                "is_liked": False,
                "created_at": "2025-12-06T10:00:00",
                "updated_at": "2025-12-06T10:00:00"
            }
        }
    }


class ReviewListResponse(BaseModel):
    """리뷰 목록 응답"""
    content: list[ReviewResponse] = Field(..., description="리뷰 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., alias="totalElements", description="전체 리뷰 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 10,
                "total_elements": 50,
                "total_pages": 5,
                "sort": "created_at,desc"
            }
        }
    }


class LikeToggleResponse(BaseModel):
    """좋아요 토글 응답"""
    is_liked: bool = Field(..., description="좋아요 상태")
    like_count: int = Field(..., description="총 좋아요 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_liked": True,
                "like_count": 16
            }
        }
    }
