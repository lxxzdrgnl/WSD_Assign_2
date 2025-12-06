"""
Favorite Models
위시리스트(즐겨찾기) 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Favorite(Base):
    """즐겨찾기(위시리스트) 테이블 (삭제 여부 추적 - 통계용)"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="즐겨찾기 ID")
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
    is_deleted = Column(Boolean, nullable=False, default=False, comment="삭제 여부 (통계용)")
    deleted_at = Column(DateTime, nullable=True, comment="삭제 일시")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")

    # Relationships
    user = relationship("User", back_populates="favorites")
    book = relationship("Book", back_populates="favorites")
