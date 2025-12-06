from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc
from app.models import Book, BookView, UserRole
from app.domains.books import schemas
from app.core.exceptions import (
    BookNotFoundException, ConflictException, ForbiddenException
)
from app.core.error_codes import ErrorCode
from typing import Optional
import math


def create_book(db: Session, request: schemas.BookCreateRequest, seller_id: int) -> schemas.BookResponse:
    existing_book = db.query(Book).filter(Book.isbn == request.isbn).first()
    if existing_book:
        raise ConflictException(
            error_code=ErrorCode.ISBN_ALREADY_EXISTS,
            message=f"Book with ISBN {request.isbn} already exists",
            details={"isbn": request.isbn}
        )

    new_book = Book(
        seller_id=seller_id,
        title=request.title,
        author=request.author,
        publisher=request.publisher,
        summary=request.summary,
        isbn=request.isbn,
        price=request.price,
        publication_date=request.publication_date
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return schemas.BookResponse.model_validate(new_book)


def get_book(db: Session, book_id: int, user_id: Optional[int] = None) -> schemas.BookResponse:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise BookNotFoundException(
            message=f"Book with ID {book_id} not found",
            details={"book_id": book_id}
        )

    view_record = BookView(user_id=user_id, book_id=book_id)
    db.add(view_record)
    db.commit()

    view_count = db.query(func.count(BookView.id)).filter(BookView.book_id == book_id).scalar()

    book_response = schemas.BookResponse.model_validate(book)
    book_response.view_count = view_count
    return book_response


def list_books(db: Session, params: schemas.BookSearchParams) -> schemas.BookListResponse:
    query = db.query(Book)

    if params.keyword:
        search_pattern = f"%{params.keyword}%"
        query = query.filter(
            or_(
                Book.title.like(search_pattern),
                Book.author.like(search_pattern),
                Book.publisher.like(search_pattern)
            )
        )

    if params.author:
        query = query.filter(Book.author.like(f"%{params.author}%"))

    if params.publisher:
        query = query.filter(Book.publisher.like(f"%{params.publisher}%"))

    if params.isbn:
        query = query.filter(Book.isbn == params.isbn)

    if params.min_price is not None:
        query = query.filter(Book.price >= params.min_price)

    if params.max_price is not None:
        query = query.filter(Book.price <= params.max_price)

    if params.start_date:
        query = query.filter(Book.publication_date >= params.start_date)

    if params.end_date:
        query = query.filter(Book.publication_date <= params.end_date)

    if params.sort == "view_count":
        subquery = db.query(
            BookView.book_id,
            func.count(BookView.id).label("view_count")
        ).group_by(BookView.book_id).subquery()

        query = query.outerjoin(subquery, Book.id == subquery.c.book_id)
        order_col = subquery.c.view_count
    else:
        order_col = getattr(Book, params.sort)

    if params.order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    total_elements = query.count()
    total_pages = math.ceil(total_elements / params.size)

    books = query.offset((params.page - 1) * params.size).limit(params.size).all()

    book_responses = []
    for book in books:
        view_count = db.query(func.count(BookView.id)).filter(BookView.book_id == book.id).scalar()
        book_response = schemas.BookResponse.model_validate(book)
        book_response.view_count = view_count
        book_responses.append(book_response)

    return schemas.BookListResponse(
        content=book_responses,
        page=params.page,
        size=params.size,
        total_elements=total_elements,
        total_pages=total_pages,
        sort=f"{params.sort},{params.order}"
    )


def update_book(
    db: Session, book_id: int, request: schemas.BookUpdateRequest, user_id: int, user_role: str
) -> schemas.BookResponse:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise BookNotFoundException(
            message=f"Book with ID {book_id} not found",
            details={"book_id": book_id}
        )

    if user_role != UserRole.ADMIN.value and book.seller_id != user_id:
        raise ForbiddenException(
            message="You can only update your own books",
            details={"book_id": book_id, "seller_id": book.seller_id}
        )

    if request.title is not None:
        book.title = request.title
    if request.author is not None:
        book.author = request.author
    if request.publisher is not None:
        book.publisher = request.publisher
    if request.summary is not None:
        book.summary = request.summary
    if request.price is not None:
        book.price = request.price
    if request.publication_date is not None:
        book.publication_date = request.publication_date

    db.commit()
    db.refresh(book)

    return schemas.BookResponse.model_validate(book)


def delete_book(db: Session, book_id: int, user_id: int, user_role: str) -> None:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise BookNotFoundException(
            message=f"Book with ID {book_id} not found",
            details={"book_id": book_id}
        )

    if user_role != UserRole.ADMIN.value and book.seller_id != user_id:
        raise ForbiddenException(
            message="You can only delete your own books",
            details={"book_id": book_id, "seller_id": book.seller_id}
        )

    db.delete(book)
    db.commit()
