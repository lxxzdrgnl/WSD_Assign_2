"""
Cart Schemas
장바구니 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CartAddRequest(BaseModel):
    """장바구니 추가 요청"""
    book_id: int = Field(..., gt=0, description="도서 ID")
    quantity: int = Field(1, ge=1, le=99, description="수량 (1-99)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "book_id": 1,
                "quantity": 2
            }
        }
    }


class CartUpdateRequest(BaseModel):
    """장바구니 수량 수정 요청"""
    quantity: int = Field(..., ge=1, le=99, description="수량 (1-99)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "quantity": 3
            }
        }
    }


class CartItemResponse(BaseModel):
    """장바구니 항목 응답"""
    id: int = Field(..., description="장바구니 ID")
    user_id: int = Field(..., description="사용자 ID")
    book_id: int = Field(..., description="도서 ID")
    book_title: str = Field(..., description="도서 제목")
    book_author: str = Field(..., description="저자")
    book_price: int = Field(..., description="가격")
    book_thumbnail: Optional[str] = Field(None, description="썸네일 URL")
    quantity: int = Field(..., description="수량")
    subtotal: int = Field(..., description="소계 (가격 * 수량)")
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
                "quantity": 2,
                "subtotal": 21600,
                "created_at": "2025-12-06T13:00:00"
            }
        }
    }


class CartListResponse(BaseModel):
    """장바구니 목록 응답"""
    items: list[CartItemResponse] = Field(..., description="장바구니 항목 목록")
    total_items: int = Field(..., description="총 항목 수")
    total_quantity: int = Field(..., description="총 수량")
    total_price: int = Field(..., description="총 금액")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [],
                "total_items": 3,
                "total_quantity": 5,
                "total_price": 75000
            }
        }
    }
