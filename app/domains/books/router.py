from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.domains.books import schemas, service
from app.domains.base import BaseResponse, SuccessResponse
from app.core.dependencies import require_seller, get_optional_user, get_sort_params
from app.core.limiter import limiter
from app.models import User

router = APIRouter(prefix="/api/books", tags=["Books"])


@router.post(
    "",
    response_model=BaseResponse[schemas.BookResponse],
    status_code=status.HTTP_201_CREATED,
    summary="도서 생성 (판매자)"
)
@limiter.limit("30/minute")
def create_book(
    data: schemas.BookCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    result = service.create_book(db, data, current_user.id)
    return BaseResponse(is_success=True, message="도서가 성공적으로 생성되었습니다.", payload=result)


@router.get(
    "/{book_id}",
    response_model=BaseResponse[schemas.BookResponse],
    summary="도서 상세 조회"
)
@limiter.limit("100/minute")
def get_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if current_user else None
    result = service.get_book(db, book_id, user_id)
    return BaseResponse(is_success=True, message="도서가 성공적으로 조회되었습니다.", payload=result)


@router.get(
    "",
    response_model=BaseResponse[schemas.BookListResponse],
    summary="도서 목록 조회"
)
@limiter.limit("100/minute")
def list_books(
    request: Request,
    keyword: Optional[str] = Query(None, description="검색 키워드"),
    author: Optional[str] = Query(None, description="작가 필터"),
    publisher: Optional[str] = Query(None, description="출판사 필터"),
    isbn: Optional[str] = Query(None, description="ISBN 필터"),
    min_price: Optional[Decimal] = Query(None, description="최소 가격"),
    max_price: Optional[Decimal] = Query(None, description="최대 가격"),
    start_date: Optional[date] = Query(None, description="시작일"),
    end_date: Optional[date] = Query(None, description="종료일"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    sort_params: Optional[tuple[str, str]] = Depends(get_sort_params(
        allowed_fields=["title", "author", "price", "publication_date", "created_at", "view_count"]
    ))
):
    sort_field, sort_order = sort_params if sort_params else ("created_at", "DESC")

    params = schemas.BookSearchParams(
        keyword=keyword,
        author=author,
        publisher=publisher,
        isbn=isbn,
        min_price=min_price,
        max_price=max_price,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size,
        sort=sort_field,
        order=sort_order
    )
    result = service.list_books(db, params)

    # 응답 스키마에 맞게 정렬 필드 추가
    payload_data = result.model_dump()
    payload_data["sort"] = f"{sort_field},{sort_order}"

    return BaseResponse(is_success=True, message="도서 목록이 성공적으로 조회되었습니다.", payload=schemas.BookListResponse(**payload_data))


@router.patch(
    "/{book_id}",
    response_model=BaseResponse[schemas.BookResponse],
    summary="도서 수정 (판매자)"
)
@limiter.limit("30/minute")
def update_book(
    book_id: int,
    data: schemas.BookUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    result = service.update_book(db, book_id, data, current_user.id, current_user.role.value)
    return BaseResponse(is_success=True, message="도서가 성공적으로 업데이트되었습니다.", payload=result)


@router.delete(
    "/{book_id}",
    response_model=SuccessResponse,
    summary="도서 삭제 (판매자)"
)
@limiter.limit("30/minute")
def delete_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    service.delete_book(db, book_id, current_user.id, current_user.role.value)
    return SuccessResponse(message="도서가 성공적으로 삭제되었습니다.")
