"""
Order Models
주문 및 주문 상세 항목 관련 모델
"""
from sqlalchemy import Column, BigInteger, Enum, DECIMAL, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """주문 상태"""
    CREATED = "CREATED"      # 주문 생성
    PAID = "PAID"            # 결제 완료
    SHIPPED = "SHIPPED"      # 배송 중
    DELIVERED = "DELIVERED"  # 배송 완료
    CANCELED = "CANCELED"    # 주문 취소


class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="주문 ID")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="주문자 ID"
    )
    total_price = Column(DECIMAL(15, 2), nullable=False, comment="총 결제 금액")
    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.CREATED,
        index=True,
        comment="주문 상태"
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="주문 생성일")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="주문 수정일"
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="order")


class OrderItem(Base):
    """주문 상세 항목 테이블"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="주문 상세 ID")
    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="주문 ID"
    )
    book_id = Column(
        BigInteger,
        ForeignKey("books.id", ondelete="SET NULL"),
        nullable=True,
        comment="도서 ID"
    )
    quantity = Column(Integer, nullable=False, comment="수량")
    price_at_purchase = Column(DECIMAL(15, 2), nullable=False, comment="구매 당시 도서 가격")

    # Relationships
    order = relationship("Order", back_populates="items")
    book = relationship("Book", back_populates="order_items")
