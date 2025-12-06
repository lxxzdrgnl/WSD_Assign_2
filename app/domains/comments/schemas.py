"""
Comments Schemas
댓글 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CommentCreateRequest(BaseModel):
    """댓글 작성 요청"""
    review_id: int = Field(..., gt=0, description="리뷰 ID")
    parent_id: Optional[int] = Field(None, gt=0, description="부모 댓글 ID (대댓글인 경우)")
    content: str = Field(..., min_length=1, max_length=500, description="댓글 내용 (1-500자)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "review_id": 1,
                "parent_id": None,
                "content": "좋은 리뷰 감사합니다!"
            }
        }
    }


class CommentUpdateRequest(BaseModel):
    """댓글 수정 요청"""
    content: str = Field(..., min_length=1, max_length=500, description="댓글 내용")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "수정된 댓글 내용입니다."
            }
        }
    }


class CommentResponse(BaseModel):
    """댓글 응답"""
    id: int = Field(..., description="댓글 ID")
    review_id: int = Field(..., description="리뷰 ID")
    user_id: int = Field(..., description="작성자 ID")
    user_name: str = Field(..., description="작성자 이름")
    parent_id: Optional[int] = Field(None, description="부모 댓글 ID")
    content: str = Field(..., description="댓글 내용")
    like_count: int = Field(0, description="좋아요 수")
    is_liked: bool = Field(False, description="현재 사용자의 좋아요 여부")
    created_at: datetime = Field(..., description="작성일")
    updated_at: datetime = Field(..., description="수정일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "review_id": 1,
                "user_id": 3,
                "user_name": "김철수",
                "parent_id": None,
                "content": "좋은 리뷰 감사합니다!",
                "like_count": 5,
                "is_liked": False,
                "created_at": "2025-12-06T11:00:00",
                "updated_at": "2025-12-06T11:00:00"
            }
        }
    }


class CommentListResponse(BaseModel):
    """댓글 목록 응답"""
    content: list[CommentResponse] = Field(..., description="댓글 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., description="전체 댓글 수")
    total_pages: int = Field(..., description="전체 페이지 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 20,
                "total_elements": 15,
                "total_pages": 1
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
                "like_count": 6
            }
        }
    }
