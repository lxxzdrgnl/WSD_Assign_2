"""
Orders Service
주문 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from app.models.order import Order, OrderItem, OrderStatus
from app.models.book import Book
from app.models.coupon import Coupon, UserCoupon
from app.domains.orders.schemas import OrderCreateRequest
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from datetime import datetime
from typing import Optional


class OrderService:
    """주문 서비스"""

    @staticmethod
    def create_order(db: Session, user_id: int, data: OrderCreateRequest) -> Order:
        """
        주문 생성

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 주문 데이터

        Returns:
            Order: 생성된 주문

        Raises:
            NotFoundException: 도서 또는 쿠폰을 찾을 수 없음
            BadRequestException: 쿠폰 사용 불가
        """
        # 주문 항목 검증 및 총 금액 계산
        total_price = 0
        order_items_data = []

        for item in data.items:
            book = db.query(Book).filter(Book.id == item.book_id).first()
            if not book:
                raise NotFoundException("BOOK_NOT_FOUND", f"Book with ID {item.book_id} not found")

            subtotal = book.price * item.quantity
            total_price += subtotal

            order_items_data.append({
                "book_id": book.id,
                "quantity": item.quantity,
                "price": book.price,
                "book_title": book.title,
                "book_author": book.author
            })

        # 쿠폰 적용
        discount_amount = 0
        coupon_code = None

        if data.coupon_id:
            coupon = db.query(Coupon).filter(Coupon.id == data.coupon_id).first()
            if not coupon:
                raise NotFoundException("COUPON_NOT_FOUND", "Coupon not found")

            # 쿠폰 유효성 검증
            if not coupon.is_active:
                raise BadRequestException("COUPON_INACTIVE", "Coupon is not active")

            now = datetime.utcnow()
            if coupon.start_at and now < coupon.start_at:
                raise BadRequestException("COUPON_NOT_YET_VALID", "Coupon is not yet valid")
            if coupon.end_at and now > coupon.end_at:
                raise BadRequestException("COUPON_EXPIRED", "Coupon has expired")

            # 사용자 쿠폰 확인
            user_coupon = db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == data.coupon_id,
                UserCoupon.used_at.is_(None)
            ).first()

            if not user_coupon:
                raise BadRequestException("COUPON_NOT_AVAILABLE", "Coupon is not available for this user")

            # 할인 금액 계산 (discount_rate는 백분율)
            discount_amount = int(total_price * float(coupon.discount_rate) / 100)

            coupon_code = coupon.name

        final_price = total_price - discount_amount
        if final_price < 0:
            final_price = 0

        # 주문 생성
        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_price=total_price,
            discount_amount=discount_amount,
            final_price=final_price,
            shipping_address=data.shipping_address
        )

        try:
            db.add(order)
            db.flush()  # ID 생성

            # 주문 항목 생성
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=item_data["book_id"],
                    quantity=item_data["quantity"],
                    price_at_purchase=item_data["price"]
                )
                db.add(order_item)

            # 쿠폰 사용 처리
            if data.coupon_id:
                user_coupon.used_at = datetime.utcnow()
                user_coupon.order_id = order.id

            db.commit()
            db.refresh(order)

        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("ORDER_CREATE_FAILED", f"Failed to create order: {str(e)}")

        # 응답용 데이터 추가
        order.coupon_code = coupon_code

        return order

    @staticmethod
    def get_orders(
        db: Session,
        user_id: int,
        status: Optional[OrderStatus] = None,
        page: int = 1,
        size: int = 10,
        sort_field: str = "created_at",
        sort_order: str = "DESC"
    ) -> tuple[list[Order], int]:
        """
        주문 목록 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            status: 주문 상태 필터 (선택)
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (주문 목록, 전체 개수)
        """
        query = db.query(Order).filter(Order.user_id == user_id)

        # 필터링
        if status:
            query = query.filter(Order.status == status)

        # 동적 정렬
        if sort_field:
            if sort_order.upper() == "DESC":
                query = query.order_by(desc(getattr(Order, sort_field)))
            else:
                query = query.order_by(getattr(Order, sort_field))

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        orders = query.offset(offset).limit(size).all()

        # 쿠폰 코드 추가
        for order in orders:
            user_coupon = db.query(UserCoupon).filter(
                UserCoupon.order_id == order.id
            ).first()
            if user_coupon:
                coupon = db.query(Coupon).filter(Coupon.id == user_coupon.coupon_id).first()
                order.coupon_code = coupon.name if coupon else None
            else:
                order.coupon_code = None

            # 주문 항목 추가
            order.items = []

        return orders, total

    @staticmethod
    def get_order(db: Session, order_id: int, user_id: int) -> Order:
        """
        주문 상세 조회

        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            user_id: 사용자 ID

        Returns:
            Order: 주문 객체

        Raises:
            NotFoundException: 주문을 찾을 수 없음
            ForbiddenException: 본인의 주문이 아님
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException("ORDER_NOT_FOUND", "Order not found")

        # 권한 확인
        if order.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only view your own orders")

        # 쿠폰 코드 추가
        user_coupon = db.query(UserCoupon).filter(UserCoupon.order_id == order.id).first()
        if user_coupon:
            coupon = db.query(Coupon).filter(Coupon.id == user_coupon.coupon_id).first()
            order.coupon_code = coupon.name if coupon else None
        else:
            order.coupon_code = None

        # 주문 항목 조회
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            book = db.query(Book).filter(Book.id == item.book_id).first()
            if book:
                item.book_title = book.title
                item.book_author = book.author
            item.subtotal = item.price_at_purchase * item.quantity

        order.items = order_items

        return order

    @staticmethod
    def cancel_order(db: Session, order_id: int, user_id: int) -> Order:
        """
        주문 취소

        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            user_id: 사용자 ID

        Returns:
            Order: 취소된 주문

        Raises:
            NotFoundException: 주문을 찾을 수 없음
            ForbiddenException: 본인의 주문이 아님
            BadRequestException: 취소할 수 없는 상태
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException("ORDER_NOT_FOUND", "Order not found")

        # 권한 확인
        if order.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only cancel your own orders")

        # 상태 확인 (PENDING, CONFIRMED만 취소 가능)
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise BadRequestException(
                "ORDER_NOT_CANCELABLE",
                f"Cannot cancel order with status {order.status}"
            )

        # 주문 취소
        order.status = OrderStatus.CANCELLED

        # 쿠폰 복구 (사용 취소)
        user_coupon = db.query(UserCoupon).filter(UserCoupon.order_id == order.id).first()
        if user_coupon:
            user_coupon.used_at = None
            user_coupon.order_id = None

        try:
            db.commit()
            db.refresh(order)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("CANCEL_FAILED", f"Failed to cancel order: {str(e)}")

        return order
