"""
Admin Router
관리자 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role, get_sort_params
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
from app.domains.base import BaseResponse, SuccessResponse
from typing import Optional
import math


router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=BaseResponse[AdminUserListResponse],
    summary="전체 사용자 목록 조회",
    description="관리자 전용: 전체 사용자 목록을 조회합니다.",
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)
def get_all_users(
    role: Optional[UserRole] = Query(None, description="역할 필터"),
    keyword: Optional[str] = Query(None, description="검색 키워드 (이메일 또는 이름)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["id", "email", "name", "created_at", "role"]
    ))
):
    """전체 사용자 목록 조회 (ADMIN)"""
    sort_field, sort_order = sort_params if sort_params else ("created_at", "DESC")

    users, total = AdminService.get_all_users(
        db=db,
        role=role,
        keyword=keyword,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )

    # 응답 데이터 구성
    user_list = [AdminUserResponse.model_validate(user) for user in users]
    total_pages = math.ceil(total / size) if total > 0 else 0

    payload_data = AdminUserListResponse(
        content=user_list,
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}"
    ).model_dump(by_alias=True) # model_dump with by_alias=True to handle camelCase

    return BaseResponse(
        is_success=True,
        message="사용자 목록을 성공적으로 조회했습니다.",
        payload=AdminUserListResponse(**payload_data)
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
        message="사용자 역할이 성공적으로 업데이트되었습니다.",
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
        message="통계를 성공적으로 조회했습니다.",
        payload=StatsResponse(**stats)
    )


@router.patch(
    "/orders/{order_id}/status",
    response_model=SuccessResponse,
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

    return SuccessResponse(
        message="주문 상태가 성공적으로 업데이트되었습니다.",
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
        message="쿠폰이 성공적으로 생성되었습니다.",
        payload=CouponResponse.model_validate(coupon)
    )


@router.post(
    "/coupons/{coupon_id}/issue/{user_id}",
    response_model=SuccessResponse,
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

    return SuccessResponse(
        message="쿠폰이 성공적으로 발급되었습니다."
    )
