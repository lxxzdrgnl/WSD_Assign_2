"""
Coupon Models
쿠폰 및 사용자 쿠폰 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, String, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Coupon(Base):
    """쿠폰 테이블"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="쿠폰 ID")
    name = Column(String(100), nullable=False, comment="쿠폰명")
    description = Column(String(255), nullable=True, comment="쿠폰 설명")
    discount_rate = Column(DECIMAL(5, 2), nullable=False, comment="할인율 (%)")
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


class UserCoupon(Base):
    """사용자 쿠폰 테이블 (발급 및 사용 현황)"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="사용자 쿠폰 ID")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    coupon_id = Column(
        BigInteger,
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="쿠폰 ID"
    )
    is_used = Column(Boolean, nullable=False, default=False, comment="사용 여부")
    used_at = Column(DateTime, nullable=True, comment="사용 일시")
    assigned_at = Column(DateTime, nullable=False, server_default=func.now(), comment="발급 일시")

    # Relationships
    user = relationship("User", back_populates="user_coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")
