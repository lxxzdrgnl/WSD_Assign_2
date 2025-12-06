"""
Comment Models
댓글 및 댓글 좋아요 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Comment(Base):
    """댓글 테이블 (리뷰에 대한 댓글)"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="댓글 ID")
    review_id = Column(
        BigInteger,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="댓글이 달린 리뷰 ID"
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="작성자 ID"
    )
    parent_comment_id = Column(
        BigInteger,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        comment="NULL이면 일반 댓글, 값이 있으면 대댓글"
    )
    content = Column(Text, nullable=False, comment="댓글 내용")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="작성일")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일"
    )

    # Relationships
    review = relationship("Review", back_populates="comments")
    user = relationship("User", back_populates="comments")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")

    # Self-referential relationship for nested comments
    parent = relationship("Comment", remote_side=[id], backref="replies")


class CommentLike(Base):
    """댓글 좋아요 테이블"""
    __tablename__ = "comment_likes"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="unique_comment_like"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="댓글 좋아요 ID")
    comment_id = Column(
        BigInteger,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="좋아요 대상 댓글 ID"
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="좋아요 누른 사용자 ID"
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="좋아요 일시")

    # Relationships
    comment = relationship("Comment", back_populates="likes")
    user = relationship("User", back_populates="comment_likes")
