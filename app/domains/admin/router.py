"""
Admin Router
관리자 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.domains.admin.schemas import (
    AdminUserResponse,
    AdminUserListResponse,
    RoleUpdateRequest,
    OrderStatusUpdateRequest,
    StatsResponse,
    CouponCreateRequest,
    CouponResponse
)
from app.domains.admin.service import AdminService
from app.domains.base import BaseResponse
from typing import Optional
import math


router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=BaseResponse[AdminUserListResponse],
    summary="전체 사용자 목록 조회",
    description="관리자 전용: 전체 사용자 목록을 조회합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def get_all_users(
    role: Optional[UserRole] = Query(None, description="역할 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """전체 사용자 목록 조회 (ADMIN)"""
    users, total = AdminService.get_all_users(
        db=db,
        role=role,
        page=page,
        size=size
    )

    # 응답 데이터 구성
    user_list = [AdminUserResponse.model_validate(user) for user in users]
    total_pages = math.ceil(total / size) if total > 0 else 0

    return BaseResponse(
        is_success=True,
        message="Users retrieved successfully",
        payload=AdminUserListResponse(
            content=user_list,
            page=page,
            size=size,
            total_elements=total,
            total_pages=total_pages
        )
    )


@router.patch(
    "/users/{user_id}/role",
    response_model=BaseResponse[AdminUserResponse],
    summary="사용자 역할 변경",
    description="관리자 전용: 사용자의 역할을 변경합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def update_user_role(
    user_id: int,
    data: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 역할 변경 (ADMIN)"""
    user = AdminService.update_user_role(db, user_id, data)

    return BaseResponse(
        is_success=True,
        message="User role updated successfully",
        payload=AdminUserResponse.model_validate(user)
    )


@router.get(
    "/stats",
    response_model=BaseResponse[StatsResponse],
    summary="통계 조회",
    description="관리자 전용: 전체 통계를 조회합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """통계 조회 (ADMIN)"""
    stats = AdminService.get_stats(db)

    return BaseResponse(
        is_success=True,
        message="Stats retrieved successfully",
        payload=StatsResponse(**stats)
    )


@router.patch(
    "/orders/{order_id}/status",
    response_model=BaseResponse[None],
    summary="주문 상태 변경",
    description="관리자 전용: 주문 상태를 변경합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 상태 변경 (ADMIN)"""
    AdminService.update_order_status(db, order_id, data)

    return BaseResponse(
        is_success=True,
        message="Order status updated successfully",
        payload=None
    )


@router.post(
    "/coupons",
    response_model=BaseResponse[CouponResponse],
    status_code=status.HTTP_201_CREATED,
    summary="쿠폰 생성",
    description="관리자 전용: 새 쿠폰을 생성합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def create_coupon(
    data: CouponCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """쿠폰 생성 (ADMIN)"""
    coupon = AdminService.create_coupon(db, data)

    return BaseResponse(
        is_success=True,
        message="Coupon created successfully",
        payload=CouponResponse.model_validate(coupon)
    )


@router.post(
    "/coupons/{coupon_id}/issue/{user_id}",
    response_model=BaseResponse[None],
    status_code=status.HTTP_201_CREATED,
    summary="쿠폰 발급",
    description="관리자 전용: 특정 사용자에게 쿠폰을 발급합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def issue_coupon(
    coupon_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """쿠폰 발급 (ADMIN)"""
    AdminService.issue_coupon_to_user(db, coupon_id, user_id)

    return BaseResponse(
        is_success=True,
        message="Coupon issued successfully",
        payload=None
    )
