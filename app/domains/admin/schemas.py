"""
Admin Schemas
관리자 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, Literal
from app.models.user import UserRole, Gender
from app.models.order import OrderStatus


class AdminUserResponse(BaseModel):
    """관리자용 사용자 응답"""
    id: int = Field(..., description="사용자 ID")
    role: UserRole = Field(..., description="사용자 역할")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="이름")
    birth_date: date = Field(..., description="생년월일")
    gender: Gender = Field(..., description="성별")
    created_at: datetime = Field(..., description="가입일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "role": "CUSTOMER",
                "email": "user@example.com",
                "name": "홍길동",
                "birth_date": "1990-01-01",
                "gender": "MALE",
                "created_at": "2025-12-01T10:00:00"
            }
        }
    }


class AdminUserListResponse(BaseModel):
    """사용자 목록 응답"""
    content: list[AdminUserResponse] = Field(..., description="사용자 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., description="전체 사용자 수")
    total_pages: int = Field(..., description="전체 페이지 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": [],
                "page": 1,
                "size": 20,
                "total_elements": 50,
                "total_pages": 3
            }
        }
    }


class RoleUpdateRequest(BaseModel):
    """역할 변경 요청"""
    role: UserRole = Field(..., description="새 역할")

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "SELLER"
            }
        }
    }


class OrderStatusUpdateRequest(BaseModel):
    """주문 상태 변경 요청"""
    status: OrderStatus = Field(..., description="새 주문 상태")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "DELIVERED"
            }
        }
    }


class StatsResponse(BaseModel):
    """통계 응답"""
    total_users: int = Field(..., description="총 사용자 수")
    total_books: int = Field(..., description="총 도서 수")
    total_orders: int = Field(..., description="총 주문 수")
    total_revenue: int = Field(..., description="총 매출")
    pending_orders: int = Field(..., description="대기 중인 주문 수")
    delivered_orders: int = Field(..., description="배송 완료 주문 수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_users": 50,
                "total_books": 100,
                "total_orders": 25,
                "total_revenue": 1250000,
                "pending_orders": 5,
                "delivered_orders": 15
            }
        }
    }


class CouponCreateRequest(BaseModel):
    """쿠폰 생성 요청"""
    code: str = Field(..., min_length=3, max_length=50, description="쿠폰 코드")
    discount_type: Literal["PERCENTAGE", "FIXED"] = Field(..., description="할인 타입 (PERCENTAGE, FIXED)")
    discount_value: int = Field(..., gt=0, description="할인 값 (퍼센트 또는 고정 금액)")
    min_order_amount: Optional[int] = Field(None, ge=0, description="최소 주문 금액")
    max_discount_amount: Optional[int] = Field(None, ge=0, description="최대 할인 금액 (PERCENTAGE일 때)")
    valid_from: Optional[datetime] = Field(None, description="유효 시작일")
    valid_until: Optional[datetime] = Field(None, description="유효 종료일")
    is_active: bool = Field(True, description="활성화 여부")

    @field_validator('discount_value')
    @classmethod
    def validate_discount_value(cls, v: int, info) -> int:
        """할인 값 검증"""
        discount_type = info.data.get('discount_type')
        if discount_type == "PERCENTAGE" and (v < 1 or v > 100):
            raise ValueError('Percentage discount must be between 1 and 100')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "WELCOME10",
                "discount_type": "PERCENTAGE",
                "discount_value": 10,
                "min_order_amount": 10000,
                "max_discount_amount": 5000,
                "valid_from": "2025-12-01T00:00:00",
                "valid_until": "2025-12-31T23:59:59",
                "is_active": True
            }
        }
    }


class CouponResponse(BaseModel):
    """쿠폰 응답"""
    id: int = Field(..., description="쿠폰 ID")
    code: str = Field(..., description="쿠폰 코드")
    discount_type: Literal["PERCENTAGE", "FIXED"] = Field(..., description="할인 타입")
    discount_value: int = Field(..., description="할인 값")
    min_order_amount: Optional[int] = Field(None, description="최소 주문 금액")
    max_discount_amount: Optional[int] = Field(None, description="최대 할인 금액")
    valid_from: Optional[datetime] = Field(None, description="유효 시작일")
    valid_until: Optional[datetime] = Field(None, description="유효 종료일")
    is_active: bool = Field(..., description="활성화 여부")
    created_at: datetime = Field(..., description="생성일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "code": "WELCOME10",
                "discount_type": "PERCENTAGE",
                "discount_value": 10,
                "min_order_amount": 10000,
                "max_discount_amount": 5000,
                "valid_from": "2025-12-01T00:00:00",
                "valid_until": "2025-12-31T23:59:59",
                "is_active": True,
                "created_at": "2025-12-01T10:00:00"
            }
        }
    }
