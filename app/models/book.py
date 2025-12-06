"""
Book Models
도서 및 조회 기록 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, String, Date, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Book(Base):
    """도서 테이블"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="도서 고유 ID")
    seller_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="판매자 ID"
    )
    title = Column(String(255), nullable=False, index=True, comment="도서명")
    author = Column(String(100), nullable=False, index=True, comment="저자")
    publisher = Column(String(100), nullable=False, comment="출판사")
    summary = Column(String(500), nullable=True, comment="요약 설명")
    isbn = Column(String(20), unique=True, nullable=False, index=True, comment="ISBN 코드")
    price = Column(DECIMAL(15, 2), nullable=False, comment="판매가")
    publication_date = Column(Date, nullable=False, comment="출판일")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="등록일시")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )

    # Relationships
    seller = relationship("User", back_populates="books", foreign_keys=[seller_id])
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="book", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="book", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="book")
    books_view = relationship("BookView", back_populates="book", cascade="all, delete-orphan")


class BookView(Base):
    """도서 조회 기록 테이블 (조회수, 인기도서 조회 사용)"""
    __tablename__ = "books_view"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="조회 기록 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="조회한 사용자 (비로그인 가능)"
    )
    book_id = Column(
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="조회된 도서"
    )
    viewed_at = Column(DateTime, nullable=False, server_default=func.now(), comment="조회 일시")

    # Relationships
    user = relationship("User", back_populates="books_view")
    book = relationship("Book", back_populates="books_view")
