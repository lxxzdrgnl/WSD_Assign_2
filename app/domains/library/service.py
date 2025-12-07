"""
Library Service
구매한 도서 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.order import Order, OrderItem, OrderStatus
from app.models.book import Book
from typing import Optional


class LibraryService:
    """라이브러리 서비스"""

    @staticmethod
    def get_purchased_books(
        db: Session,
        user_id: int,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_field: str = "order_date", # Default sort to 'order_date' for library
        sort_order: str = "DESC"
    ) -> tuple[list[dict], int]:
        """
        구매한 도서 목록 조회 (DELIVERED 상태)

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (구매한 도서 목록, 전체 개수)
        """
        # DELIVERED 상태인 주문의 항목만 조회
        query = db.query(OrderItem, Order, Book).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Book, OrderItem.book_id == Book.id
        ).filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.DELIVERED
        )

        # 필터링
        if keyword:
            query = query.filter(
                (Book.title.ilike(f"%{keyword}%")) |
                (Book.author.ilike(f"%{keyword}%"))
            )

        # 동적 정렬
        if sort_field:
            if sort_field == "order_date":
                model_field = Order.created_at # Map 'order_date' to Order.created_at
            else: # title, author
                model_field = getattr(Book, sort_field)

            if sort_order.upper() == "DESC":
                query = query.order_by(desc(model_field))
            else:
                query = query.order_by(model_field)

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        results = query.offset(offset).limit(size).all()

        # 응답 데이터 구성
        books = []
        for order_item, order, book in results:
            books.append({
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "thumbnail_url": None,  # Book 모델에 thumbnail_url 필드 없음
                "purchased_at": order.created_at,
                "order_id": order.id
            })

        return books, total
