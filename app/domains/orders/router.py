"""
Orders Router
주문 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_sort_params
from app.models.user import User
from app.models.order import OrderStatus
from app.domains.orders.schemas import (
    OrderCreateRequest,
    OrderResponse,
    OrderListResponse,
    OrderItemResponse
)
from app.domains.orders.service import OrderService
from app.domains.base import BaseResponse
from typing import Optional
import math


router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post(
    "",
    response_model=BaseResponse[OrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="주문 생성",
    description="주문을 생성합니다. 쿠폰을 적용할 수 있습니다."
)
def create_order(
    data: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 생성"""
    order = OrderService.create_order(db, current_user.id, data)

    # 주문 항목 조회
    order = OrderService.get_order(db, order.id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="주문이 성공적으로 생성되었습니다.",
        payload=OrderResponse.model_validate(order)
    )


@router.get(
    "",
    response_model=BaseResponse[OrderListResponse],
    summary="주문 목록 조회",
    description="내 주문 목록을 조회합니다. 상태별 필터링을 지원합니다."
)
def get_orders(
    status: Optional[OrderStatus] = Query(None, description="주문 상태 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["id", "created_at", "status", "total_price"]
    ))
):
    """주문 목록 조회"""
    sort_field, sort_order = sort_params if sort_params else ("created_at", "desc")

    orders, total = OrderService.get_orders(
        db=db,
        user_id=current_user.id,
        status=status,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )

    # 응답 데이터 구성
    order_list = [OrderResponse.model_validate(order) for order in orders]
    total_pages = math.ceil(total / size) if total > 0 else 0

    payload_data = OrderListResponse(
        content=order_list,
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}"
    ).model_dump(by_alias=True)

    return BaseResponse(
        is_success=True,
        message="주문 목록이 성공적으로 조회되었습니다.",
        payload=OrderListResponse(**payload_data)
    )


@router.get(
    "/{order_id}",
    response_model=BaseResponse[OrderResponse],
    summary="주문 상세 조회",
    description="특정 주문의 상세 정보를 조회합니다."
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 상세 조회"""
    order = OrderService.get_order(db, order_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="주문이 성공적으로 조회되었습니다.",
        payload=OrderResponse.model_validate(order)
    )


@router.patch(
    "/{order_id}/cancel",
    response_model=BaseResponse[OrderResponse],
    summary="주문 취소",
    description="주문을 취소합니다. PENDING, CONFIRMED 상태에서만 취소 가능합니다."
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """주문 취소"""
    order = OrderService.cancel_order(db, order_id, current_user.id)

    # 주문 상세 재조회
    order = OrderService.get_order(db, order.id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="주문이 성공적으로 취소되었습니다.",
        payload=OrderResponse.model_validate(order)
    )
