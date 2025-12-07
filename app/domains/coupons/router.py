from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.core.database import get_db
from app.domains.coupons import schemas, service
from app.domains.base import BaseResponse
from app.core.dependencies import get_current_user, get_sort_params
from app.models import User

router = APIRouter(prefix="/api/coupons", tags=["Coupons"])


@router.get(
    "",
    response_model=BaseResponse[schemas.CouponListResponse],
    summary="사용 가능한 쿠폰 조회",
    description="현재 사용 가능한 활성화된 쿠폰 목록을 조회합니다."
)
def get_available_coupons(
    keyword: Optional[str] = Query(None, description="검색 키워드 (쿠폰 이름 또는 설명)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["name", "discount_rate", "start_at", "end_at", "created_at"]
    ))
):
    """
    사용 가능한 쿠폰 목록 조회

    - **인증 불필요**: 누구나 조회 가능
    - **필터링**: 활성화되고 유효기간 내의 쿠폰만 표시
    """
    sort_field, sort_order = sort_params if sort_params else ("created_at", "desc")

    coupons, total = service.get_available_coupons(
        db=db,
        keyword=keyword,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )

    total_pages = math.ceil(total / size) if total > 0 else 0
    payload_data = schemas.CouponListResponse(
        content=[schemas.CouponResponse.model_validate(c) for c in coupons],
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}"
    ).model_dump(by_alias=True)

    return BaseResponse(
        is_success=True,
        message="사용 가능한 쿠폰 목록이 성공적으로 조회되었습니다.",
        payload=schemas.CouponListResponse(**payload_data)
    )


@router.get(
    "/my",
    response_model=BaseResponse[schemas.MyCouponListResponse],
    summary="내 쿠폰 조회",
    description="내가 보유한 쿠폰 목록을 조회합니다. 사용 여부로 필터링 가능합니다."
)
def get_my_coupons(
    is_used: Optional[bool] = Query(None, description="사용 여부 필터 (true: 사용됨, false: 미사용, null: 전체)"),
    keyword: Optional[str] = Query(None, description="검색 키워드 (쿠폰 이름 또는 설명)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["coupon_name", "discount_rate", "assigned_at", "used_at", "start_at", "end_at"]
    ))
):
    """
    내 쿠폰 목록 조회

    - **인증 필요**: JWT Access Token
    - **권한**: 모든 로그인 사용자
    - **필터링**: is_used 파라미터로 사용/미사용 필터링
    """
    sort_field, sort_order = sort_params if sort_params else ("assigned_at", "desc")

    coupons, total = service.get_my_coupons(
        db=db,
        user_id=current_user.id,
        is_used=is_used,
        keyword=keyword,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )
    unused_count = sum(1 for c in coupons if not c["is_used"])

    total_pages = math.ceil(total / size) if total > 0 else 0
    payload_data = schemas.MyCouponListResponse(
        content=[schemas.UserCouponResponse.model_validate(c) for c in coupons],
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}",
        unused_count=unused_count
    ).model_dump(by_alias=True)

    return BaseResponse(
        is_success=True,
        message="내 쿠폰 목록이 성공적으로 조회되었습니다.",
        payload=schemas.MyCouponListResponse(**payload_data)
    )
