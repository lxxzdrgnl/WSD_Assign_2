"""
Reviews Service
리뷰 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from sqlalchemy.exc import IntegrityError
from app.models.review import Review, ReviewLike, ReviewLikeCount
from app.models.book import Book
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from app.domains.reviews.schemas import ReviewCreateRequest, ReviewUpdateRequest
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from typing import Optional


class ReviewService:
    """리뷰 서비스"""

    @staticmethod
    def verify_purchase(db: Session, user_id: int, book_id: int) -> Optional[int]:
        """
        도서 구매 검증

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            book_id: 도서 ID

        Returns:
            Optional[int]: 구매한 주문 ID, 구매하지 않았으면 None
        """
        # DELIVERED 상태인 주문에서 해당 도서를 포함하는지 확인
        purchased = db.query(Order).join(OrderItem).filter(
            Order.user_id == user_id,
            OrderItem.book_id == book_id,
            Order.status == OrderStatus.DELIVERED
        ).first()

        return purchased.id if purchased else None

    @staticmethod
    def create_review(db: Session, user_id: int, data: ReviewCreateRequest) -> Review:
        """
        리뷰 작성 (구매 검증 필요)

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 리뷰 데이터

        Returns:
            Review: 생성된 리뷰

        Raises:
            NotFoundException: 도서를 찾을 수 없음
            ForbiddenException: 구매하지 않은 도서
        """
        # 도서 존재 확인
        book = db.query(Book).filter(Book.id == data.book_id).first()
        if not book:
            raise NotFoundException("BOOK_NOT_FOUND", "Book not found")

        # 구매 검증
        order_id = ReviewService.verify_purchase(db, user_id, data.book_id)
        if not order_id:
            raise ForbiddenException(
                "REVIEW_REQUIRES_PURCHASE",
                "You can only review books you have purchased and received"
            )

        # 중복 리뷰 체크 (친절한 에러 메시지 제공)
        existing_review = db.query(Review).filter(
            Review.user_id == user_id,
            Review.book_id == data.book_id
        ).first()
        if existing_review:
            raise BadRequestException(
                "DUPLICATE_REVIEW",
                f"You have already reviewed this book (Review ID: {existing_review.id}). Please update your existing review instead."
            )

        # 리뷰 생성
        review = Review(
            book_id=data.book_id,
            user_id=user_id,
            order_id=order_id,
            rating=data.rating,
            comment=data.content
        )

        try:
            db.add(review)
            db.commit()
            db.refresh(review)

            # 좋아요 카운트 테이블 초기화
            like_count = ReviewLikeCount(review_id=review.id, like_count=0)
            db.add(like_count)
            db.commit()

        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("REVIEW_CREATE_FAILED", f"Failed to create review: {str(e)}")

        return review

    @staticmethod
    def get_reviews(
        db: Session,
        current_user_id: Optional[int],
        book_id: Optional[int] = None,
        user_id: Optional[int] = None,
        min_rating: Optional[int] = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        size: int = 10
    ) -> tuple[list[Review], int]:
        """
        리뷰 목록 조회 (좋아요 순 Top-N 지원)

        Args:
            db: 데이터베이스 세션
            current_user_id: 현재 사용자 ID (선택)
            book_id: 도서 ID 필터 (선택)
            user_id: 작성자 ID 필터 (선택)
            min_rating: 최소 평점 필터 (선택)
            sort: 정렬 기준
            order: 정렬 순서
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (리뷰 목록, 전체 개수)
        """
        query = db.query(Review)

        # 필터링
        if book_id:
            query = query.filter(Review.book_id == book_id)
        if user_id:
            query = query.filter(Review.user_id == user_id)
        if min_rating:
            query = query.filter(Review.rating >= min_rating)

        # 정렬
        if sort == "like_count":
            # 좋아요 수로 정렬 시 ReviewLikeCount 테이블 조인
            query = query.join(ReviewLikeCount, Review.id == ReviewLikeCount.review_id)
            order_by = desc(ReviewLikeCount.like_count) if order == "desc" else asc(ReviewLikeCount.like_count)
        elif sort == "rating":
            order_by = desc(Review.rating) if order == "desc" else asc(Review.rating)
        else:  # created_at (기본값)
            order_by = desc(Review.created_at) if order == "desc" else asc(Review.created_at)

        query = query.order_by(order_by)

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        reviews = query.offset(offset).limit(size).all()

        # 현재 사용자의 좋아요 여부 및 좋아요 수 추가
        for review in reviews:
            # 좋아요 수 (캐시에서 조회)
            like_count_obj = db.query(ReviewLikeCount).filter(
                ReviewLikeCount.review_id == review.id
            ).first()
            review.like_count = like_count_obj.like_count if like_count_obj else 0

            # 현재 사용자의 좋아요 여부
            if current_user_id:
                is_liked = db.query(ReviewLike).filter(
                    ReviewLike.review_id == review.id,
                    ReviewLike.user_id == current_user_id
                ).first() is not None
                review.is_liked = is_liked
            else:
                review.is_liked = False

            # 작성자 이름 추가
            user = db.query(User).filter(User.id == review.user_id).first()
            review.user_name = user.name if user else "Unknown"

        return reviews, total

    @staticmethod
    def get_review(db: Session, review_id: int, current_user_id: Optional[int]) -> Review:
        """
        리뷰 상세 조회

        Args:
            db: 데이터베이스 세션
            review_id: 리뷰 ID
            current_user_id: 현재 사용자 ID (선택)

        Returns:
            Review: 리뷰 객체

        Raises:
            NotFoundException: 리뷰를 찾을 수 없음
        """
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundException("REVIEW_NOT_FOUND", "Review not found")

        # 좋아요 수
        like_count_obj = db.query(ReviewLikeCount).filter(
            ReviewLikeCount.review_id == review.id
        ).first()
        review.like_count = like_count_obj.like_count if like_count_obj else 0

        # 현재 사용자의 좋아요 여부
        if current_user_id:
            is_liked = db.query(ReviewLike).filter(
                ReviewLike.review_id == review.id,
                ReviewLike.user_id == current_user_id
            ).first() is not None
            review.is_liked = is_liked
        else:
            review.is_liked = False

        # 작성자 이름
        user = db.query(User).filter(User.id == review.user_id).first()
        review.user_name = user.name if user else "Unknown"

        return review

    @staticmethod
    def update_review(db: Session, review_id: int, user_id: int, data: ReviewUpdateRequest) -> Review:
        """
        리뷰 수정 (본인만 가능)

        Args:
            db: 데이터베이스 세션
            review_id: 리뷰 ID
            user_id: 사용자 ID
            data: 수정할 데이터

        Returns:
            Review: 수정된 리뷰

        Raises:
            NotFoundException: 리뷰를 찾을 수 없음
            ForbiddenException: 본인의 리뷰가 아님
            BadRequestException: 수정할 내용이 없음
        """
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundException("REVIEW_NOT_FOUND", "Review not found")

        # 권한 확인
        if review.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only update your own reviews")

        # 수정할 필드만 업데이트
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("NO_FIELDS_TO_UPDATE", "No fields to update")

        # content -> comment 필드 매핑
        if 'content' in update_data:
            update_data['comment'] = update_data.pop('content')

        for field, value in update_data.items():
            setattr(review, field, value)

        try:
            db.commit()
            db.refresh(review)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("UPDATE_FAILED", f"Failed to update review: {str(e)}")

        return review

    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int) -> None:
        """
        리뷰 삭제 (본인만 가능)

        Args:
            db: 데이터베이스 세션
            review_id: 리뷰 ID
            user_id: 사용자 ID

        Raises:
            NotFoundException: 리뷰를 찾을 수 없음
            ForbiddenException: 본인의 리뷰가 아님
        """
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundException("REVIEW_NOT_FOUND", "Review not found")

        # 권한 확인
        if review.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only delete your own reviews")

        # CASCADE로 관련 데이터 자동 삭제 (review_likes, review_like_counts, comments)
        db.delete(review)
        db.commit()

    @staticmethod
    def toggle_like(db: Session, review_id: int, user_id: int) -> tuple[bool, int]:
        """
        리뷰 좋아요 토글

        Args:
            db: 데이터베이스 세션
            review_id: 리뷰 ID
            user_id: 사용자 ID

        Returns:
            tuple: (좋아요 상태, 총 좋아요 수)

        Raises:
            NotFoundException: 리뷰를 찾을 수 없음
        """
        # 리뷰 존재 확인
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundException("REVIEW_NOT_FOUND", "Review not found")

        # 기존 좋아요 확인
        existing_like = db.query(ReviewLike).filter(
            ReviewLike.review_id == review_id,
            ReviewLike.user_id == user_id
        ).first()

        is_liked = False

        if existing_like:
            # 좋아요 취소
            db.delete(existing_like)
        else:
            # 좋아요 추가
            new_like = ReviewLike(review_id=review_id, user_id=user_id)
            db.add(new_like)
            is_liked = True

        db.commit()

        # 좋아요 수 업데이트 (캐시 테이블)
        like_count_obj = db.query(ReviewLikeCount).filter(
            ReviewLikeCount.review_id == review_id
        ).first()

        if not like_count_obj:
            # 캐시가 없으면 생성
            current_count = db.query(func.count(ReviewLike.id)).filter(
                ReviewLike.review_id == review_id
            ).scalar()
            like_count_obj = ReviewLikeCount(review_id=review_id, like_count=current_count)
            db.add(like_count_obj)
        else:
            # 캐시 업데이트
            current_count = db.query(func.count(ReviewLike.id)).filter(
                ReviewLike.review_id == review_id
            ).scalar()
            like_count_obj.like_count = current_count

        db.commit()

        return is_liked, like_count_obj.like_count
