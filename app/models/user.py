"""
User Models
사용자 및 인증 관련 모델
"""
from sqlalchemy import Column, BigInteger, Integer, String, Enum, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """사용자 역할"""
    CUSTOMER = "CUSTOMER"
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class Gender(str, enum.Enum):
    """성별"""
    MALE = "MALE"
    FEMALE = "FEMALE"


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="사용자 고유 ID")
    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.CUSTOMER,
        comment="사용자 역할 (CUSTOMER, SELLER, ADMIN)"
    )
    email = Column(String(255), unique=True, nullable=False, index=True, comment="이메일 (로그인 ID)")
    password = Column(String(255), nullable=False, comment="비밀번호 (암호화)")
    name = Column(String(255), nullable=False, comment="이름")
    birth_date = Column(Date, nullable=False, comment="생년월일")
    gender = Column(Enum(Gender), nullable=False, comment="성별")
    address = Column(String(255), nullable=True, comment="주소")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정일시"
    )

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    books = relationship("Book", back_populates="seller", foreign_keys="Book.seller_id")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    user_coupons = relationship("UserCoupon", back_populates="user", cascade="all, delete-orphan")
    review_likes = relationship("ReviewLike", back_populates="user", cascade="all, delete-orphan")
    comment_likes = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    books_view = relationship("BookView", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """Refresh Token 테이블"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Refresh Token 고유 ID")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="토큰 사용자 ID"
    )
    token = Column(String(500), unique=True, nullable=False, index=True, comment="발급된 Refresh Token 문자열")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="토큰 생성시간")
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="토큰 정보 수정시간"
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
