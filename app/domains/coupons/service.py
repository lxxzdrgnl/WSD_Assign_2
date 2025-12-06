from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.coupon import Coupon, UserCoupon
from app.domains.coupons import schemas
from app.core.exceptions import BaseAPIException
from fastapi import status


def get_available_coupons(db: Session) -> list[Coupon]:
    """
    현재 사용 가능한 활성화된 쿠폰 목록 조회
    """
    now = datetime.utcnow()
    coupons = db.query(Coupon).filter(
        and_(
            Coupon.is_active == True,
            Coupon.start_at <= now,
            Coupon.end_at >= now
        )
    ).order_by(Coupon.created_at.desc()).all()

    return coupons


def get_my_coupons(db: Session, user_id: int, is_used: bool = None) -> list[dict]:
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
        Coupon.discount_type,
        Coupon.discount_value,
        Coupon.max_discount_amount,
        Coupon.min_order_amount,
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

    results = query.order_by(UserCoupon.assigned_at.desc()).all()

    # Convert to dict
    coupons = []
    for row in results:
        coupons.append({
            "id": row.id,
            "coupon_id": row.coupon_id,
            "coupon_name": row.coupon_name,
            "description": row.description,
            "discount_type": row.discount_type,
            "discount_value": row.discount_value,
            "max_discount_amount": row.max_discount_amount,
            "min_order_amount": row.min_order_amount,
            "is_used": row.is_used,
            "used_at": row.used_at,
            "assigned_at": row.assigned_at,
            "start_at": row.start_at,
            "end_at": row.end_at,
            "is_active": row.is_active
        })

    return coupons
