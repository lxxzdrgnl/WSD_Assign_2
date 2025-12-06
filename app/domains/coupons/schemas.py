from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CouponResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    discount_rate: float
    start_at: datetime
    end_at: datetime
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "신규회원10",
                "description": "신규회원10 쿠폰 - 10% 할인",
                "discount_rate": 10.0,
                "start_at": "2025-12-01T00:00:00",
                "end_at": "2026-12-01T23:59:59",
                "is_active": True,
                "created_at": "2025-12-01T00:00:00"
            }
        }
    }


class UserCouponResponse(BaseModel):
    id: int
    coupon_id: int
    coupon_name: str
    description: Optional[str] = None
    discount_rate: float
    is_used: bool
    used_at: Optional[datetime] = None
    assigned_at: datetime
    start_at: datetime
    end_at: datetime
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "coupon_id": 1,
                "coupon_name": "신규회원10",
                "description": "신규회원10 쿠폰 - 10% 할인",
                "discount_rate": 10.0,
                "is_used": False,
                "used_at": None,
                "assigned_at": "2025-12-01T00:00:00",
                "start_at": "2025-12-01T00:00:00",
                "end_at": "2026-12-01T23:59:59",
                "is_active": True
            }
        }
    }


class CouponListResponse(BaseModel):
    content: list[CouponResponse]
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., alias="totalElements", description="전체 쿠폰 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": [
                    {
                        "id": 1,
                        "name": "신규회원10",
                        "description": "신규회원10 쿠폰 - 10% 할인",
                        "discount_rate": 10.0,
                        "start_at": "2025-01-01T00:00:00",
                        "end_at": "2025-12-31T23:59:59",
                        "is_active": True,
                        "created_at": "2025-01-01T00:00:00"
                    }
                ],
                "total": 1
            }
        }
    }


class MyCouponListResponse(BaseModel):
    content: list[UserCouponResponse]
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_elements: int = Field(..., alias="totalElements", description="전체 쿠폰 수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 수")
    sort: str = Field(..., description="정렬 기준")
    unused_count: int

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "content": [],
                "total": 0,
                "unused_count": 0
            }
        }
    }
