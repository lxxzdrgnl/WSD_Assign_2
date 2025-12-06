"""
Users Service
사용자 프로필 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.domains.users.schemas import UserUpdateRequest
from app.core.security import hash_password
from app.core.exceptions import NotFoundError, BadRequestError


class UserService:
    """사용자 프로필 서비스"""

    @staticmethod
    def get_profile(db: Session, user_id: int) -> User:
        """
        프로필 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            User: 사용자 객체

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "User not found")

        return user

    @staticmethod
    def update_profile(db: Session, user_id: int, data: UserUpdateRequest) -> User:
        """
        프로필 수정

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 수정할 데이터

        Returns:
            User: 수정된 사용자 객체

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
            BadRequestError: 수정할 내용이 없음
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "User not found")

        # 수정할 필드만 업데이트
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise BadRequestError("NO_FIELDS_TO_UPDATE", "No fields to update")

        # 비밀번호는 해싱 필요
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        # 필드 업데이트
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestError("UPDATE_FAILED", f"Failed to update profile: {str(e)}")

        return user

    @staticmethod
    def delete_account(db: Session, user_id: int) -> None:
        """
        계정 삭제 (물리 삭제)

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID

        Raises:
            NotFoundError: 사용자를 찾을 수 없음
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("USER_NOT_FOUND", "User not found")

        # CASCADE 설정으로 관련 데이터 자동 삭제
        # - refresh_tokens
        # - reviews
        # - comments
        # - favorites
        # - carts
        # - user_coupons
        # - review_likes
        # - comment_likes
        # - books_view
        db.delete(user)
        db.commit()
