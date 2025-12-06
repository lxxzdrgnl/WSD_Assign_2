"""
Books Domain Tests
도서 관련 엔드포인트 테스트
"""
import pytest
from decimal import Decimal


class TestBooks:
    """도서 테스트"""

    def test_get_books_list(self, client, test_db):
        """도서 목록 조회 테스트"""
        from app.models import Book
        from datetime import datetime

        # 테스트용 도서 생성
        books = [
            Book(
                title=f"Test Book {i}",
                author="Test Author",
                publisher="Test Publisher",
                price=Decimal("10000"),
                stock=100,
                genre="FICTION",
                description="Test description",
                isbn=f"978000000000{i}",
                published_date=datetime.now()
            )
            for i in range(5)
        ]
        test_db.add_all(books)
        test_db.commit()

        # 도서 목록 조회
        response = client.get("/api/books")

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert "content" in payload
        assert len(payload["content"]) == 5

    def test_get_book_detail(self, client, test_db):
        """도서 상세 조회 테스트"""
        from app.models import Book
        from datetime import datetime

        # 테스트용 도서 생성
        book = Book(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            price=Decimal("15000"),
            stock=50,
            genre="FICTION",
            description="Test description",
            isbn="9780000000001",
            published_date=datetime.now()
        )
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)

        # 도서 상세 조회
        response = client.get(f"/api/books/{book.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert payload["title"] == "Test Book"
        assert payload["author"] == "Test Author"

    def test_get_book_not_found(self, client):
        """존재하지 않는 도서 조회 실패 테스트"""
        response = client.get("/api/books/99999")

        assert response.status_code == 404

    def test_create_book_seller(self, client, seller_token, test_db):
        """판매자의 도서 등록 테스트"""
        response = client.post(
            "/api/books",
            headers={"Authorization": f"Bearer {seller_token}"},
            json={
                "title": "New Book",
                "author": "New Author",
                "publisher": "New Publisher",
                "price": 20000,
                "stock": 100,
                "genre": "SCIENCE",
                "description": "A new science book",
                "isbn": "9781234567890",
                "published_date": "2025-01-01T00:00:00"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert payload["title"] == "New Book"
        assert "book_id" in payload

    def test_create_book_customer_forbidden(self, client, customer_token):
        """고객의 도서 등록 실패 테스트 (권한 없음)"""
        response = client.post(
            "/api/books",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "title": "New Book",
                "author": "New Author",
                "publisher": "New Publisher",
                "price": 20000,
                "stock": 100,
                "genre": "SCIENCE",
                "description": "A new science book",
                "isbn": "9781234567890",
                "published_date": "2025-01-01T00:00:00"
            }
        )

        assert response.status_code == 403

    def test_update_book_seller(self, client, seller_token, test_db):
        """판매자의 도서 수정 테스트"""
        from app.models import Book
        from datetime import datetime

        # 테스트용 도서 생성
        book = Book(
            title="Original Title",
            author="Original Author",
            publisher="Original Publisher",
            price=Decimal("10000"),
            stock=50,
            genre="FICTION",
            description="Original description",
            isbn="9780000000002",
            published_date=datetime.now()
        )
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)

        # 도서 수정
        response = client.patch(
            f"/api/books/{book.id}",
            headers={"Authorization": f"Bearer {seller_token}"},
            json={
                "title": "Updated Title",
                "author": "Updated Author",
                "publisher": "Updated Publisher",
                "price": 15000,
                "stock": 75,
                "genre": "NON_FICTION",
                "description": "Updated description",
                "isbn": "9780000000002",
                "published_date": "2025-01-01T00:00:00"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True

    def test_delete_book_seller(self, client, seller_token, test_db):
        """판매자의 도서 삭제 테스트"""
        from app.models import Book
        from datetime import datetime

        # 테스트용 도서 생성
        book = Book(
            title="To Be Deleted",
            author="Test Author",
            publisher="Test Publisher",
            price=Decimal("10000"),
            stock=50,
            genre="FICTION",
            description="Test description",
            isbn="9780000000003",
            published_date=datetime.now()
        )
        test_db.add(book)
        test_db.commit()
        test_db.refresh(book)

        # 도서 삭제
        response = client.delete(
            f"/api/books/{book.id}",
            headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True

        # 삭제된 도서 조회 시 404
        response = client.get(f"/api/books/{book.id}")
        assert response.status_code == 404
