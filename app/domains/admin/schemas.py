"""
Admin Schemas
관리자 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, Literal
from app.models.user import UserRole, Gender
from app.models.order import OrderStatus
from app.models.coupon import CouponType


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
                "role": "ADMIN",
                "email": "admin@bookstore.com",
                "name": "관리자",
                "birth_date": "1980-01-01",
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
    total_elements: int = Field(..., alias="totalElements", description="전체 사용자 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")

    model_config = {
        "populate_by_name": True,
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
    name: str = Field(..., min_length=3, max_length=100, description="쿠폰 이름")
    description: Optional[str] = Field(None, max_length=255, description="쿠폰 설명")
    discount_rate: float = Field(..., gt=0, lt=100, description="할인율 (%)")
    start_at: datetime = Field(..., description="유효 시작일")
    end_at: datetime = Field(..., description="유효 종료일")
    is_active: bool = Field(True, description="활성화 여부")
    issue_to_all: bool = Field(False, description="모든 사용자에게 발급 여부")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "크리스마스 전체 할인",
                "description": "모든 회원 대상 크리스마스 특별 할인 쿠폰",
                "discount_rate": 20.0,
                "start_at": "2025-12-25T00:00:00",
                "end_at": "2025-12-25T23:59:59",
                "is_active": True,
                "issue_to_all": True
            }
        }
    }


class CouponResponse(BaseModel):
    """쿠폰 응답"""
    id: int = Field(..., description="쿠폰 ID")
    name: str = Field(..., description="쿠폰 이름")
    description: Optional[str] = Field(None, description="쿠폰 설명")
    discount_rate: float = Field(..., description="할인율 (%)")
    coupon_type: CouponType = Field(..., description="쿠폰 타입 (UNIVERSAL: 전체, PERSONAL: 개인)")
    start_at: datetime = Field(..., description="유효 시작일")
    end_at: datetime = Field(..., description="유효 종료일")
    is_active: bool = Field(..., description="활성화 여부")
    created_at: datetime = Field(..., description="생성일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "크리스마스 전체 할인",
                "description": "모든 회원 대상 크리스마스 특별 할인 쿠폰",
                "discount_rate": 20.0,
                "coupon_type": "UNIVERSAL",
                "start_at": "2025-12-25T00:00:00",
                "end_at": "2025-12-25T23:59:59",
                "is_active": True,
                "created_at": "2025-12-14T12:00:00"
            }
        }
    }
