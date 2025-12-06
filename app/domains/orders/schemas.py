"""
Orders Schemas
주문 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.order import OrderStatus


class OrderItemRequest(BaseModel):
    """주문 항목 요청"""
    book_id: int = Field(..., gt=0, description="도서 ID")
    quantity: int = Field(..., ge=1, le=99, description="수량")


class OrderCreateRequest(BaseModel):
    """주문 생성 요청"""
    items: List[OrderItemRequest] = Field(..., min_length=1, description="주문 항목 목록")
    coupon_id: Optional[int] = Field(None, description="쿠폰 ID (선택)")
    shipping_address: str = Field(..., min_length=5, max_length=255, description="배송지 주소")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {"book_id": 1, "quantity": 2},
                    {"book_id": 2, "quantity": 1}
                ],
                "coupon_id": 1,
                "shipping_address": "서울시 강남구 테헤란로 123"
            }
        }
    }


class OrderItemResponse(BaseModel):
    """주문 항목 응답"""
    id: int = Field(..., description="주문 항목 ID")
    book_id: int = Field(..., description="도서 ID")
    book_title: str = Field(..., description="도서 제목")
    book_author: str = Field(..., description="저자")
    quantity: int = Field(..., description="수량")
    price: int = Field(..., description="단가")
    subtotal: int = Field(..., description="소계")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "book_id": 1,
                "book_title": "채식주의자",
                "book_author": "한강",
                "quantity": 2,
                "price": 10800,
                "subtotal": 21600
            }
        }
    }


class OrderResponse(BaseModel):
    """주문 응답"""
    id: int = Field(..., description="주문 ID")
    user_id: int = Field(..., description="사용자 ID")
    status: OrderStatus = Field(..., description="주문 상태")
    total_price: int = Field(..., description="총 금액")
    discount_amount: int = Field(0, description="할인 금액")
    final_price: int = Field(..., description="최종 금액")
    shipping_address: str = Field(..., description="배송지 주소")
    coupon_code: Optional[str] = Field(None, description="사용한 쿠폰 코드")
    items: List[OrderItemResponse] = Field([], description="주문 항목 목록")
    created_at: datetime = Field(..., description="주문일")
    updated_at: datetime = Field(..., description="수정일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 11,
                "status": "PENDING",
                "total_price": 45000,
                "discount_amount": 4500,
                "final_price": 40500,
                "shipping_address": "서울시 강남구 테헤란로 123",
                "coupon_code": "신규회원10",
                "items": [],
                "created_at": "2025-12-06T14:00:00",
                "updated_at": "2025-12-06T14:00:00"
            }
        }
    }


class OrderListResponse(BaseModel):
    """주문 목록 응답"""
    content: list[OrderResponse] = Field(..., description="주문 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., alias="totalElements", description="전체 주문 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 10,
                "total_elements": 25,
                "total_pages": 3
            }
        }
    }
