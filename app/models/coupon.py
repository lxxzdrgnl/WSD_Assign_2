"""
Coupon Models
쿠폰 및 사용자 쿠폰 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, String, DECIMAL, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class CouponType(enum.Enum):
    """쿠폰 타입"""
    UNIVERSAL = "UNIVERSAL"  # 전체 사용자 대상
    PERSONAL = "PERSONAL"    # 개인 발급


class Coupon(Base):
    """쿠폰 테이블"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="쿠폰 ID")
    name = Column(String(100), nullable=False, comment="쿠폰명")
    description = Column(String(255), nullable=True, comment="쿠폰 설명")
    discount_rate = Column(DECIMAL(5, 2), nullable=False, comment="할인율 (%)")
    coupon_type = Column(
        Enum(CouponType),
        nullable=False,
        default=CouponType.PERSONAL,
        comment="쿠폰 타입 (UNIVERSAL: 전체, PERSONAL: 개인)"
    )
    start_at = Column(DateTime, nullable=False, server_default=func.now(), comment="시작 일시")
    end_at = Column(DateTime, nullable=False, comment="종료 일시")
    is_active = Column(Boolean, nullable=False, default=True, comment="활성화 여부")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )

    # Relationships
    user_coupons = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")
    issuances = relationship("CouponIssuance", back_populates="coupon", cascade="all, delete-orphan")
    usages = relationship("CouponUsageHistory", back_populates="coupon", cascade="all, delete-orphan")


class CouponIssuance(Base):
    """쿠폰 발급 테이블 (PERSONAL 쿠폰만)"""
    __tablename__ = "coupon_issuances"
    __table_args__ = (
        UniqueConstraint('user_id', 'coupon_id', name='unique_user_coupon_issuance'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="발급 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    coupon_id = Column(
        Integer,
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="쿠폰 ID"
    )
    issued_at = Column(DateTime, nullable=False, server_default=func.now(), comment="발급 일시")

    # Relationships
    user = relationship("User", back_populates="coupon_issuances")
    coupon = relationship("Coupon", back_populates="issuances")


class CouponUsageHistory(Base):
    """쿠폰 사용 이력 테이블 (모든 쿠폰)"""
    __tablename__ = "coupon_usage_history"
    __table_args__ = (
        UniqueConstraint('user_id', 'coupon_id', name='unique_user_coupon_usage'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="사용 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    coupon_id = Column(
        Integer,
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="쿠폰 ID"
    )
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        comment="사용된 주문 ID"
    )
    used_at = Column(DateTime, nullable=False, server_default=func.now(), comment="사용 일시")

    # Relationships
    user = relationship("User", back_populates="coupon_usages")
    coupon = relationship("Coupon", back_populates="usages")


class UserCoupon(Base):
    """사용자 쿠폰 테이블 (Deprecated - 기존 데이터 호환용)"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="사용자 쿠폰 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    coupon_id = Column(
        Integer,
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="쿠폰 ID"
    )
    is_used = Column(Boolean, nullable=False, default=False, comment="사용 여부")
    used_at = Column(DateTime, nullable=True, comment="사용 일시")
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, comment="사용된 주문 ID")
    assigned_at = Column(DateTime, nullable=False, server_default=func.now(), comment="발급 일시")

    # Relationships
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")
