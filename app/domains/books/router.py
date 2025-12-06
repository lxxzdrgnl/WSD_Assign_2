from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.domains.books import schemas, service
from app.schemas.base import BaseResponse, SuccessResponse
from app.core.dependencies import require_seller, get_optional_user
from app.models import User

router = APIRouter(prefix="/api/v1/books", tags=["Books"])


@router.post(
    "",
    response_model=BaseResponse[schemas.BookResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Book (SELLER)"
)
def create_book(
    request: schemas.BookCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    result = service.create_book(db, request, current_user.id)
    return BaseResponse(isSuccess=True, message="Book created successfully", payload=result)


@router.get(
    "/{book_id}",
    response_model=BaseResponse[schemas.BookResponse],
    summary="Get Book Detail"
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    user_id = current_user.id if current_user else None
    result = service.get_book(db, book_id, user_id)
    return BaseResponse(isSuccess=True, message="Book retrieved successfully", payload=result)


@router.get(
    "",
    response_model=BaseResponse[schemas.BookListResponse],
    summary="List Books"
)
def list_books(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    author: Optional[str] = Query(None, description="Author filter"),
    publisher: Optional[str] = Query(None, description="Publisher filter"),
    isbn: Optional[str] = Query(None, description="ISBN filter"),
    min_price: Optional[Decimal] = Query(None, description="Min price"),
    max_price: Optional[Decimal] = Query(None, description="Max price"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort order"),
    db: Session = Depends(get_db)
):
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
        sort=sort,
        order=order
    )
    result = service.list_books(db, params)
    return BaseResponse(isSuccess=True, message="Books retrieved successfully", payload=result)


@router.patch(
    "/{book_id}",
    response_model=BaseResponse[schemas.BookResponse],
    summary="Update Book (SELLER)"
)
def update_book(
    book_id: int,
    request: schemas.BookUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    result = service.update_book(db, book_id, request, current_user.id, current_user.role.value)
    return BaseResponse(isSuccess=True, message="Book updated successfully", payload=result)


@router.delete(
    "/{book_id}",
    response_model=SuccessResponse,
    summary="Delete Book (SELLER)"
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller)
):
    service.delete_book(db, book_id, current_user.id, current_user.role.value)
    return SuccessResponse(message="Book deleted successfully")
