"""
Review Models
리뷰, 리뷰 좋아요, 리뷰 좋아요 캐시 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    """리뷰 테이블"""
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="리뷰 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="작성자 ID"
    )
    book_id = Column(
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="리뷰 대상 도서"
    )
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="실제 구매한 주문 ID"
    )
    comment = Column(Text, nullable=False, comment="리뷰 내용")
    rating = Column(Integer, nullable=False, comment="평점 (1~5)")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="작성일")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일"
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")
    likes = relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")
    like_count = relationship("ReviewLikeCount", back_populates="review", uselist=False, cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="review", cascade="all, delete-orphan")


class ReviewLike(Base):
    """리뷰 좋아요 테이블"""
    __tablename__ = "review_likes"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="unique_review_like"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="리뷰 좋아요 ID")
    review_id = Column(
        Integer,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="좋아요 대상 리뷰 ID"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="좋아요 누른 사용자 ID"
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="좋아요 일시")

    # Relationships
    review = relationship("Review", back_populates="likes")
    user = relationship("User", back_populates="review_likes")


class ReviewLikeCount(Base):
    """리뷰 좋아요 수 캐시 테이블 (N-Top 성능 최적화)"""
    __tablename__ = "review_like_counts"

    review_id = Column(
        Integer,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        primary_key=True,
        comment="리뷰 ID"
    )
    like_count = Column(Integer, nullable=False, default=0, comment="좋아요 수 캐시")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="마지막 업데이트 일시"
    )

    # Relationships
    review = relationship("Review", back_populates="like_count")
