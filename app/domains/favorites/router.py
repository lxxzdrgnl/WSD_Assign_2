"""
Favorites Router
위시리스트 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.domains.favorites.schemas import (
    FavoriteAddRequest,
    FavoriteResponse,
    FavoriteListResponse
)
from app.domains.favorites.service import FavoriteService
from app.domains.base import BaseResponse
import math


router = APIRouter(prefix="/api/v1/favorites", tags=["Favorites"])


@router.post(
    "",
    response_model=BaseResponse[FavoriteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="위시리스트 추가",
    description="도서를 위시리스트에 추가합니다."
)
def add_favorite(
    data: FavoriteAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """위시리스트 추가"""
    favorite = FavoriteService.add_favorite(db, current_user.id, data)

    # 도서 정보 추가
    from app.models.book import Book
    book = db.query(Book).filter(Book.id == data.book_id).first()
    if book:
        favorite.book_title = book.title
        favorite.book_author = book.author
        favorite.book_price = book.price
        favorite.book_thumbnail = book.thumbnail_url

    return BaseResponse(
        is_success=True,
        message="Favorite added successfully",
        payload=FavoriteResponse.model_validate(favorite)
    )


@router.get(
    "",
    response_model=BaseResponse[FavoriteListResponse],
    summary="위시리스트 조회",
    description="내 위시리스트를 조회합니다."
)
def get_favorites(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """위시리스트 조회"""
    favorites, total = FavoriteService.get_favorites(
        db=db,
        user_id=current_user.id,
        page=page,
        size=size
    )

    # 응답 데이터 구성
    favorite_list = [FavoriteResponse.model_validate(favorite) for favorite in favorites]
    total_pages = math.ceil(total / size) if total > 0 else 0

    return BaseResponse(
        is_success=True,
        message="Favorites retrieved successfully",
        payload=FavoriteListResponse(
            content=favorite_list,
            page=page,
            size=size,
            total_elements=total,
            total_pages=total_pages
        )
    )


@router.delete(
    "/{favorite_id}",
    response_model=BaseResponse[None],
    summary="위시리스트 삭제",
    description="위시리스트에서 도서를 삭제합니다."
)
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """위시리스트 삭제"""
    FavoriteService.delete_favorite(db, favorite_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Favorite deleted successfully",
        payload=None
    )
