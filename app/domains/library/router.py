"""
Library Router
구매한 도서 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.domains.library.schemas import LibraryBookResponse, LibraryListResponse
from app.domains.library.service import LibraryService
from app.domains.base import BaseResponse
import math


router = APIRouter(prefix="/api/v1/library", tags=["Library"])


@router.get(
    "",
    response_model=BaseResponse[LibraryListResponse],
    summary="구매한 도서 목록 조회",
    description="배송 완료(DELIVERED) 상태인 주문의 도서 목록을 조회합니다."
)
def get_library(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """구매한 도서 목록 조회"""
    books, total = LibraryService.get_purchased_books(
        db=db,
        user_id=current_user.id,
        page=page,
        size=size
    )

    # 응답 데이터 구성
    book_list = [LibraryBookResponse(**book) for book in books]
    total_pages = math.ceil(total / size) if total > 0 else 0

    return BaseResponse(
        is_success=True,
        message="Library retrieved successfully",
        payload=LibraryListResponse(
            content=book_list,
            page=page,
            size=size,
            total_elements=total,
            total_pages=total_pages
        )
    )
