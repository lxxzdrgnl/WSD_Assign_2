"""
Favorites Service
위시리스트 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from app.models.favorite import Favorite
from app.models.book import Book
from app.domains.favorites.schemas import FavoriteAddRequest
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException


class FavoriteService:
    """위시리스트 서비스"""

    @staticmethod
    def add_favorite(db: Session, user_id: int, data: FavoriteAddRequest) -> Favorite:
        """
        위시리스트 추가

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 도서 ID

        Returns:
            Favorite: 생성된 위시리스트

        Raises:
            NotFoundException: 도서를 찾을 수 없음
            ConflictException: 이미 위시리스트에 추가됨
        """
        # 도서 존재 확인
        book = db.query(Book).filter(Book.id == data.book_id).first()
        if not book:
            raise NotFoundException("BOOK_NOT_FOUND", "Book not found")

        # 이미 위시리스트에 있는지 확인 (삭제되지 않은 항목)
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.book_id == data.book_id,
            Favorite.deleted_at.is_(None)
        ).first()

        if existing:
            raise ConflictException("ALREADY_IN_FAVORITES", "Book is already in your favorites")

        # 위시리스트 추가
        favorite = Favorite(
            user_id=user_id,
            book_id=data.book_id
        )

        try:
            db.add(favorite)
            db.commit()
            db.refresh(favorite)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("FAVORITE_ADD_FAILED", f"Failed to add favorite: {str(e)}")

        return favorite

    @staticmethod
    def get_favorites(
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 20
    ) -> tuple[list[Favorite], int]:
        """
        위시리스트 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (위시리스트 목록, 전체 개수)
        """
        # 삭제되지 않은 항목만 조회
        query = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.deleted_at.is_(None)
        )

        # 정렬 (최근 추가순)
        query = query.order_by(desc(Favorite.created_at))

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        favorites = query.offset(offset).limit(size).all()

        # 도서 정보 추가
        for favorite in favorites:
            book = db.query(Book).filter(Book.id == favorite.book_id).first()
            if book:
                favorite.book_title = book.title
                favorite.book_author = book.author
                favorite.book_price = book.price
                favorite.book_thumbnail = book.thumbnail_url

        return favorites, total

    @staticmethod
    def delete_favorite(db: Session, favorite_id: int, user_id: int) -> None:
        """
        위시리스트 삭제 (논리 삭제)

        Args:
            db: 데이터베이스 세션
            favorite_id: 위시리스트 ID
            user_id: 사용자 ID

        Raises:
            NotFoundException: 위시리스트를 찾을 수 없음
            ForbiddenException: 본인의 위시리스트가 아님
        """
        from app.core.exceptions import ForbiddenException

        favorite = db.query(Favorite).filter(
            Favorite.id == favorite_id,
            Favorite.deleted_at.is_(None)
        ).first()

        if not favorite:
            raise NotFoundException("FAVORITE_NOT_FOUND", "Favorite not found")

        # 권한 확인
        if favorite.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only delete your own favorites")

        # 논리 삭제
        from datetime import datetime
        favorite.deleted_at = datetime.utcnow()

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("DELETE_FAILED", f"Failed to delete favorite: {str(e)}")
