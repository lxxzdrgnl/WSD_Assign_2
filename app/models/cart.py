"""
Cart Models
장바구니 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Cart(Base):
    """장바구니 테이블 (수량 수정, 삭제 저장 - 통계용)"""
    __tablename__ = "carts"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="장바구니 ID")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    book_id = Column(
        BigInteger,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="도서 ID"
    )
    quantity = Column(Integer, nullable=False, default=1, comment="수량")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="삭제 여부 (통계용)")
    deleted_at = Column(DateTime, nullable=True, comment="삭제 일시")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )

    # Relationships
    user = relationship("User", back_populates="carts")
    book = relationship("Book", back_populates="carts")
