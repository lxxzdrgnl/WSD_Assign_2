"""
Admin Service
관리자 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
from app.models.book import Book
from app.models.order import Order, OrderStatus
from app.models.coupon import Coupon, UserCoupon
from app.domains.admin.schemas import (
    RoleUpdateRequest,
    OrderStatusUpdateRequest,
    CouponCreateRequest
)
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError


class AdminService:
    """관리자 서비스"""

    @staticmethod
    def get_all_users(
        db: Session,
        role: UserRole = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[list[User], int]:
        """
        전체 사용자 목록 조회

        Args:
            db: 데이터베이스 세션
            role: 역할 필터 (선택)
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (사용자 목록, 전체 개수)
        """
        query = db.query(User)

        # 필터링
        if role:
            query = query.filter(User.role == role)

        # 정렬 (최신 가입순)
        query = query.order_by(desc(User.created_at))

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        users = query.offset(offset).limit(size).all()

        return users, total

    @staticmethod
    def update_user_role(db: Session, user_id: int, data: RoleUpdateRequest) -> User:
        """
        사용자 역할 변경

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 새 역할

        Returns:
            User: 수정된 사용자

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "User not found")

        # 역할 변경
        user.role = data.role

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestError("UPDATE_FAILED", f"Failed to update user role: {str(e)}")

        return user

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        통계 조회

        Args:
            db: 데이터베이스 세션

        Returns:
            dict: 통계 데이터
        """
        # 총 사용자 수
        total_users = db.query(func.count(User.id)).scalar()

        # 총 도서 수
        total_books = db.query(func.count(Book.id)).scalar()

        # 총 주문 수
        total_orders = db.query(func.count(Order.id)).scalar()

        # 총 매출 (DELIVERED 상태 주문의 최종 금액 합계)
        total_revenue = db.query(func.sum(Order.final_price)).filter(
            Order.status == OrderStatus.DELIVERED
        ).scalar() or 0

        # 대기 중인 주문 수
        pending_orders = db.query(func.count(Order.id)).filter(
            Order.status == OrderStatus.PENDING
        ).scalar()

        # 배송 완료 주문 수
        delivered_orders = db.query(func.count(Order.id)).filter(
            Order.status == OrderStatus.DELIVERED
        ).scalar()

        return {
            "total_users": total_users,
            "total_books": total_books,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders
        }

    @staticmethod
    def update_order_status(db: Session, order_id: int, data: OrderStatusUpdateRequest) -> Order:
        """
        주문 상태 변경

        Args:
            db: 데이터베이스 세션
            order_id: 주문 ID
            data: 새 주문 상태

        Returns:
            Order: 수정된 주문

        Raises:
            NotFoundError: 주문을 찾을 수 없음
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError("ORDER_NOT_FOUND", "Order not found")

        # 주문 상태 변경
        order.status = data.status

        try:
            db.commit()
            db.refresh(order)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestError("UPDATE_FAILED", f"Failed to update order status: {str(e)}")

        return order

    @staticmethod
    def create_coupon(db: Session, data: CouponCreateRequest) -> Coupon:
        """
        쿠폰 생성

        Args:
            db: 데이터베이스 세션
            data: 쿠폰 데이터

        Returns:
            Coupon: 생성된 쿠폰

        Raises:
            ConflictError: 쿠폰 코드 중복
        """
        # 쿠폰 코드 중복 확인
        existing = db.query(Coupon).filter(Coupon.code == data.code).first()
        if existing:
            raise ConflictError("COUPON_CODE_ALREADY_EXISTS", "Coupon code already exists")

        # 쿠폰 생성
        coupon = Coupon(
            code=data.code,
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            min_order_amount=data.min_order_amount,
            max_discount_amount=data.max_discount_amount,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_active=data.is_active
        )

        try:
            db.add(coupon)
            db.commit()
            db.refresh(coupon)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestError("COUPON_CREATE_FAILED", f"Failed to create coupon: {str(e)}")

        return coupon

    @staticmethod
    def issue_coupon_to_user(db: Session, coupon_id: int, user_id: int) -> UserCoupon:
        """
        사용자에게 쿠폰 발급

        Args:
            db: 데이터베이스 세션
            coupon_id: 쿠폰 ID
            user_id: 사용자 ID

        Returns:
            UserCoupon: 발급된 쿠폰

        Raises:
            NotFoundError: 쿠폰 또는 사용자를 찾을 수 없음
            ConflictError: 이미 발급됨
        """
        # 쿠폰 존재 확인
        coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            raise NotFoundError("COUPON_NOT_FOUND", "Coupon not found")

        # 사용자 존재 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "User not found")

        # 이미 발급되었는지 확인
        existing = db.query(UserCoupon).filter(
            UserCoupon.user_id == user_id,
            UserCoupon.coupon_id == coupon_id
        ).first()
        if existing:
            raise ConflictError("COUPON_ALREADY_ISSUED", "Coupon already issued to this user")

        # 쿠폰 발급
        user_coupon = UserCoupon(
            user_id=user_id,
            coupon_id=coupon_id
        )

        try:
            db.add(user_coupon)
            db.commit()
            db.refresh(user_coupon)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestError("COUPON_ISSUE_FAILED", f"Failed to issue coupon: {str(e)}")

        return user_coupon
