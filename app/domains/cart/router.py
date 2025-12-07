"""
Cart Router
장바구니 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.domains.cart.schemas import (
    CartAddRequest,
    CartUpdateRequest,
    CartItemResponse,
    CartListResponse
)
from app.domains.cart.service import CartService
from app.domains.base import BaseResponse, SuccessResponse


router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post(
    "",
    response_model=BaseResponse[CartItemResponse],
    status_code=status.HTTP_201_CREATED,
    summary="장바구니 추가",
    description="도서를 장바구니에 추가합니다. 이미 있는 경우 수량이 증가합니다."
)
def add_to_cart(
    data: CartAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """장바구니 추가"""
    cart_item = CartService.add_to_cart(db, current_user.id, data)

    # 도서 정보 추가
    from app.models.book import Book
    book = db.query(Book).filter(Book.id == data.book_id).first()
    if book:
        cart_item.book_title = book.title
        cart_item.book_author = book.author
        cart_item.book_price = book.price
        cart_item.book_thumbnail = None  # Book 모델에 thumbnail_url 필드 없음
        cart_item.subtotal = book.price * cart_item.quantity

    return BaseResponse(
        is_success=True,
        message="장바구니에 성공적으로 추가되었습니다.",
        payload=CartItemResponse.model_validate(cart_item)
    )


@router.get(
    "",
    response_model=BaseResponse[CartListResponse],
    summary="장바구니 조회",
    description="내 장바구니를 조회합니다."
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """장바구니 조회"""
    cart_items, total_items, total_quantity, total_price = CartService.get_cart(
        db=db,
        user_id=current_user.id
    )

    # 응답 데이터 구성
    item_list = [CartItemResponse.model_validate(item) for item in cart_items]

    return BaseResponse(
        is_success=True,
        message="장바구니를 성공적으로 조회했습니다.",
        payload=CartListResponse(
            items=item_list,
            total_items=total_items,
            total_quantity=total_quantity,
            total_price=total_price
        )
    )


@router.patch(
    "/{cart_item_id}",
    response_model=BaseResponse[CartItemResponse],
    summary="수량 수정",
    description="장바구니 항목의 수량을 수정합니다."
)
def update_quantity(
    cart_item_id: int,
    data: CartUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """수량 수정"""
    cart_item = CartService.update_quantity(db, cart_item_id, current_user.id, data)

    # 도서 정보 추가
    from app.models.book import Book
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    if book:
        cart_item.book_title = book.title
        cart_item.book_author = book.author
        cart_item.book_price = book.price
        cart_item.book_thumbnail = None  # Book 모델에 thumbnail_url 필드 없음
        cart_item.subtotal = book.price * cart_item.quantity

    return BaseResponse(
        is_success=True,
        message="장바구니가 성공적으로 업데이트되었습니다.",
        payload=CartItemResponse.model_validate(cart_item)
    )


@router.delete(
    "/{cart_item_id}",
    response_model=SuccessResponse,
    summary="항목 삭제",
    description="장바구니에서 항목을 삭제합니다."
)
def delete_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """항목 삭제"""
    CartService.delete_from_cart(db, cart_item_id, current_user.id)

    return SuccessResponse(
        message="장바구니 항목이 성공적으로 삭제되었습니다.",
    )
