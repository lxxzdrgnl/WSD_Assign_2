from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
from app.models.coupon import Coupon, UserCoupon
from app.domains.coupons import schemas
from app.core.exceptions import BaseAPIException
from fastapi import status
from typing import Optional


def get_available_coupons(
    db: Session,
    keyword: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    sort_field: str = "created_at",
    sort_order: str = "DESC"
) -> tuple[list[Coupon], int]:
    """
    현재 사용 가능한 활성화된 쿠폰 목록 조회
    """
    now = datetime.utcnow()
    query = db.query(Coupon).filter(
        and_(
            Coupon.is_active == True,
            Coupon.start_at <= now,
            Coupon.end_at >= now
        )
    )

    # 필터링
    if keyword:
        query = query.filter(
            (Coupon.name.ilike(f"%{keyword}%")) |
            (Coupon.description.ilike(f"%{keyword}%"))
        )
    
    # 동적 정렬
    if sort_field:
        if sort_order.upper() == "DESC":
            query = query.order_by(getattr(Coupon, sort_field).desc())
        else:
            query = query.order_by(getattr(Coupon, sort_field))
    
    # 전체 개수
    total = query.count()

    # 페이지네이션
    offset = (page - 1) * size
    coupons = query.offset(offset).limit(size).all()

    return coupons, total


def get_my_coupons(
    db: Session,
    user_id: int,
    is_used: bool = None,
    keyword: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    sort_field: str = "assigned_at",
    sort_order: str = "DESC"
) -> tuple[list[dict], int]:
    """
    내가 보유한 쿠폰 목록 조회 (사용/미사용 필터링 가능)
    """
    query = db.query(
        UserCoupon.id,
        UserCoupon.coupon_id,
        UserCoupon.is_used,
        UserCoupon.used_at,
        UserCoupon.assigned_at,
        Coupon.name.label("coupon_name"),
        Coupon.description,
        Coupon.discount_rate,
        Coupon.start_at,
        Coupon.end_at,
        Coupon.is_active
    ).join(
        Coupon, UserCoupon.coupon_id == Coupon.id
    ).filter(
        UserCoupon.user_id == user_id
    )

    if is_used is not None:
        query = query.filter(UserCoupon.is_used == is_used)

    # 필터링
    if keyword:
        query = query.filter(
            (Coupon.name.ilike(f"%{keyword}%")) |
            (Coupon.description.ilike(f"%{keyword}%"))
        )

    # 동적 정렬
    if sort_field:
        if sort_field in ["coupon_name", "discount_rate", "start_at", "end_at"]:
            model_field = getattr(Coupon, sort_field.replace("coupon_", ""))
        else: # UserCoupon 모델 필드
            model_field = getattr(UserCoupon, sort_field)
        
        if sort_order.upper() == "DESC":
            query = query.order_by(model_field.desc())
        else:
            query = query.order_by(model_field)

    # 전체 개수
    total = query.count()

    # 페이지네이션
    offset = (page - 1) * size
    results = query.offset(offset).limit(size).all()

    # Convert to dict
    coupons = []
    for row in results:
        coupons.append({
            "id": row.id,
            "coupon_id": row.coupon_id,
            "coupon_name": row.coupon_name,
            "description": row.description,
            "discount_rate": row.discount_rate,
            "is_used": row.is_used,
            "used_at": row.used_at,
            "assigned_at": row.assigned_at,
            "start_at": row.start_at,
            "end_at": row.end_at,
            "is_active": row.is_active
        })

    return coupons, total
