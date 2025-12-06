"""
Favorites Router
위시리스트 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_sort_params
from app.models.user import User
from app.domains.favorites.schemas import (
    FavoriteAddRequest,
    FavoriteResponse,
    FavoriteListResponse
)
from app.domains.favorites.service import FavoriteService
from app.domains.base import BaseResponse, SuccessResponse
import math


router = APIRouter(prefix="/api/favorites", tags=["Favorites"])


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
        message="위시리스트에 성공적으로 추가되었습니다.",
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
    keyword: Optional[str] = Query(None, description="검색 키워드 (도서 제목 또는 저자)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["book_title", "created_at"]
    ))
):
    """위시리스트 조회"""
    sort_field, sort_order = sort_params if sort_params else ("created_at", "desc")

    favorites, total = FavoriteService.get_favorites(
        db=db,
        user_id=current_user.id,
        keyword=keyword,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )

    # 응답 데이터 구성
    favorite_list = [FavoriteResponse.model_validate(favorite) for favorite in favorites]
    total_pages = math.ceil(total / size) if total > 0 else 0

    payload_data = FavoriteListResponse(
        content=favorite_list,
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}"
    ).model_dump(by_alias=True)

    return BaseResponse(
        is_success=True,
        message="위시리스트를 성공적으로 조회했습니다.",
        payload=FavoriteListResponse(**payload_data)
    )


@router.delete(
    "/{favorite_id}",
    response_model=SuccessResponse,
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

    return SuccessResponse(
        message="위시리스트에서 성공적으로 삭제되었습니다."
    )
