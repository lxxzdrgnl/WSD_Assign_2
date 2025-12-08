"""
Library Router
구매한 도서 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_sort_params
from app.models.user import User
from app.domains.library.schemas import LibraryBookResponse, LibraryListResponse
from app.domains.library.service import LibraryService
from app.domains.base import BaseResponse
import math


router = APIRouter(prefix="/api/library", tags=["Library"])


@router.get(
    "",
    response_model=BaseResponse[LibraryListResponse],
    summary="구매한 도서 목록 조회",
    description="배송 완료(DELIVERED) 상태인 주문의 도서 목록을 조회합니다."
)
def get_library(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    keyword: Optional[str] = Query(None, description="검색 키워드 (도서 제목 또는 저자)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["title", "author", "order_date"]
    ))
):
    """구매한 도서 목록 조회"""
    sort_field, sort_order = sort_params if sort_params else ("order_date", "desc")

    books, total = LibraryService.get_purchased_books(
        db=db,
        user_id=current_user.id,
        keyword=keyword,
        page=page,
        size=size,
        sort_field=sort_field,
        sort_order=sort_order
    )

    # 응답 데이터 구성
    book_list = [LibraryBookResponse(**book) for book in books]
    total_pages = math.ceil(total / size) if total > 0 else 0

    payload_data = LibraryListResponse(
        content=book_list,
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
        sort=f"{sort_field},{sort_order}"
    ).model_dump(by_alias=True)

    return BaseResponse(
        is_success=True,
        message="구매한 도서 목록이 성공적으로 조회되었습니다.",
        payload=LibraryListResponse(**payload_data)
    )
