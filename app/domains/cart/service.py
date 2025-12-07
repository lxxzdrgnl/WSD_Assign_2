"""
Cart Service
장바구니 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from app.models.cart import Cart
from app.models.book import Book
from app.domains.cart.schemas import CartAddRequest, CartUpdateRequest
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException, ConflictException


class CartService:
    """장바구니 서비스"""

    @staticmethod
    def add_to_cart(db: Session, user_id: int, data: CartAddRequest) -> Cart:
        """
        장바구니 추가

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 도서 ID 및 수량

        Returns:
            Cart: 생성된 장바구니 항목

        Raises:
            NotFoundException: 도서를 찾을 수 없음
            ConflictException: 이미 장바구니에 추가됨
        """
        # 도서 존재 확인
        book = db.query(Book).filter(Book.id == data.book_id).first()
        if not book:
            raise NotFoundException("BOOK_NOT_FOUND", "Book not found")

        # 이미 장바구니에 있는지 확인 (삭제되지 않은 항목)
        existing = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.book_id == data.book_id,
            Cart.deleted_at.is_(None)
        ).first()

        if existing:
            # 수량 업데이트
            existing.quantity += data.quantity
            db.commit()
            db.refresh(existing)
            return existing

        # 장바구니 추가
        cart_item = Cart(
            user_id=user_id,
            book_id=data.book_id,
            quantity=data.quantity
        )

        try:
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("CART_ADD_FAILED", f"Failed to add to cart: {str(e)}")

        return cart_item

    @staticmethod
    def get_cart(db: Session, user_id: int) -> tuple[list[Cart], int, int, int]:
        """
        장바구니 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            tuple: (장바구니 항목 목록, 총 항목 수, 총 수량, 총 금액)
        """
        # 삭제되지 않은 항목만 조회
        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.deleted_at.is_(None)
        ).order_by(desc(Cart.created_at)).all()

        total_items = len(cart_items)
        total_quantity = 0
        total_price = 0

        # 도서 정보 및 소계 추가
        for item in cart_items:
            book = db.query(Book).filter(Book.id == item.book_id).first()
            if book:
                item.book_title = book.title
                item.book_author = book.author
                item.book_price = book.price
                item.book_thumbnail = None  # Book 모델에 thumbnail_url 필드 없음
                item.subtotal = book.price * item.quantity

                total_quantity += item.quantity
                total_price += item.subtotal

        return cart_items, total_items, total_quantity, total_price

    @staticmethod
    def update_quantity(db: Session, cart_id: int, user_id: int, data: CartUpdateRequest) -> Cart:
        """
        장바구니 수량 수정

        Args:
            db: 데이터베이스 세션
            cart_id: 장바구니 ID
            user_id: 사용자 ID
            data: 수정할 수량

        Returns:
            Cart: 수정된 장바구니 항목

        Raises:
            NotFoundException: 장바구니 항목을 찾을 수 없음
            ForbiddenException: 본인의 장바구니가 아님
        """
        cart_item = db.query(Cart).filter(
            Cart.id == cart_id,
            Cart.deleted_at.is_(None)
        ).first()

        if not cart_item:
            raise NotFoundException("CART_ITEM_NOT_FOUND", "Cart item not found")

        # 권한 확인
        if cart_item.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only update your own cart")

        # 수량 업데이트
        cart_item.quantity = data.quantity

        try:
            db.commit()
            db.refresh(cart_item)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("UPDATE_FAILED", f"Failed to update cart: {str(e)}")

        return cart_item

    @staticmethod
    def delete_from_cart(db: Session, cart_id: int, user_id: int) -> None:
        """
        장바구니 항목 삭제 (논리 삭제)

        Args:
            db: 데이터베이스 세션
            cart_id: 장바구니 ID
            user_id: 사용자 ID

        Raises:
            NotFoundException: 장바구니 항목을 찾을 수 없음
            ForbiddenException: 본인의 장바구니가 아님
        """
        cart_item = db.query(Cart).filter(
            Cart.id == cart_id,
            Cart.deleted_at.is_(None)
        ).first()

        if not cart_item:
            raise NotFoundException("CART_ITEM_NOT_FOUND", "Cart item not found")

        # 권한 확인
        if cart_item.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only delete your own cart items")

        # 논리 삭제
        from datetime import datetime
        cart_item.deleted_at = datetime.utcnow()

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("DELETE_FAILED", f"Failed to delete cart item: {str(e)}")
