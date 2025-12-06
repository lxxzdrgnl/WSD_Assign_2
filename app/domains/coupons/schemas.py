from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class CouponResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    discount_type: str  # PERCENTAGE or FIXED
    discount_value: Decimal
    max_discount_amount: Optional[int] = None
    min_order_amount: Optional[int] = None
    start_at: datetime
    end_at: datetime
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "신규 회원 10% 할인",
                "description": "첫 구매 시 10% 할인",
                "discount_type": "PERCENTAGE",
                "discount_value": 10.0,
                "max_discount_amount": 5000,
                "min_order_amount": 10000,
                "start_at": "2025-01-01T00:00:00",
                "end_at": "2025-12-31T23:59:59",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00"
            }
        }
    }


class UserCouponResponse(BaseModel):
    id: int
    coupon_id: int
    coupon_name: str
    description: Optional[str] = None
    discount_type: str
    discount_value: Decimal
    max_discount_amount: Optional[int] = None
    min_order_amount: Optional[int] = None
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
                "coupon_name": "신규 회원 10% 할인",
                "description": "첫 구매 시 10% 할인",
                "discount_type": "PERCENTAGE",
                "discount_value": 10.0,
                "max_discount_amount": 5000,
                "min_order_amount": 10000,
                "is_used": False,
                "used_at": None,
                "assigned_at": "2025-01-01T00:00:00",
                "start_at": "2025-01-01T00:00:00",
                "end_at": "2025-12-31T23:59:59",
                "is_active": True
            }
        }
    }


class CouponListResponse(BaseModel):
    content: list[CouponResponse]
    total: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": [
                    {
                        "id": 1,
                        "name": "신규 회원 10% 할인",
                        "description": "첫 구매 시 10% 할인",
                        "discount_type": "PERCENTAGE",
                        "discount_value": 10.0,
                        "max_discount_amount": 5000,
                        "min_order_amount": 10000,
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
    total: int
    unused_count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": [],
                "total": 0,
                "unused_count": 0
            }
        }
    }
