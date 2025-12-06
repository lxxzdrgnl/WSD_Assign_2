from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.coupons import schemas, service
from app.schemas.base import BaseResponse
from app.core.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/coupons", tags=["Coupons"])


@router.get(
    "",
    response_model=BaseResponse[schemas.CouponListResponse],
    summary="Get Available Coupons",
    description="현재 사용 가능한 활성화된 쿠폰 목록을 조회합니다."
)
def get_available_coupons(
    db: Session = Depends(get_db)
):
    """
    사용 가능한 쿠폰 목록 조회

    - **인증 불필요**: 누구나 조회 가능
    - **필터링**: 활성화되고 유효기간 내의 쿠폰만 표시
    """
    coupons = service.get_available_coupons(db)

    return BaseResponse(
        isSuccess=True,
        message="Available coupons retrieved successfully",
        payload=schemas.CouponListResponse(
            content=[schemas.CouponResponse.model_validate(c) for c in coupons],
            total=len(coupons)
        )
    )


@router.get(
    "/my",
    response_model=BaseResponse[schemas.MyCouponListResponse],
    summary="Get My Coupons",
    description="내가 보유한 쿠폰 목록을 조회합니다. 사용 여부로 필터링 가능합니다."
)
def get_my_coupons(
    is_used: Optional[bool] = Query(None, description="사용 여부 필터 (true: 사용됨, false: 미사용, null: 전체)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 쿠폰 목록 조회

    - **인증 필요**: JWT Access Token
    - **권한**: 모든 로그인 사용자
    - **필터링**: is_used 파라미터로 사용/미사용 필터링
    """
    coupons = service.get_my_coupons(db, current_user.id, is_used)
    unused_count = sum(1 for c in coupons if not c["is_used"])

    return BaseResponse(
        isSuccess=True,
        message="My coupons retrieved successfully",
        payload=schemas.MyCouponListResponse(
            content=[schemas.UserCouponResponse.model_validate(c) for c in coupons],
            total=len(coupons),
            unused_count=unused_count
        )
    )
