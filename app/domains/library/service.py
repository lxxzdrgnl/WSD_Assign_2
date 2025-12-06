"""
Library Service
구매한 도서 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.order import Order, OrderItem, OrderStatus
from app.models.book import Book


class LibraryService:
    """라이브러리 서비스"""

    @staticmethod
    def get_purchased_books(
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 20
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
        ).order_by(desc(Order.created_at))

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
                "thumbnail_url": book.thumbnail_url,
                "purchased_at": order.created_at,
                "order_id": order.id
            })

        return books, total
