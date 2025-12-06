"""
Reviews Router
리뷰 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.domains.reviews.schemas import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewResponse,
    ReviewListResponse,
    LikeToggleResponse
)
from app.domains.reviews.service import ReviewService
from app.domains.base import BaseResponse
from typing import Optional
import math


router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])


@router.post(
    "",
    response_model=BaseResponse[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="리뷰 작성",
    description="도서 리뷰를 작성합니다. 구매한 도서만 리뷰 작성이 가능합니다."
)
def create_review(
    data: ReviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 작성 (구매 검증)"""
    review = ReviewService.create_review(db, current_user.id, data)

    # 응답 데이터 구성
    review.like_count = 0
    review.is_liked = False
    review.user_name = current_user.name

    return BaseResponse(
        is_success=True,
        message="Review created successfully",
        payload=ReviewResponse.model_validate(review)
    )


@router.get(
    "",
    response_model=BaseResponse[ReviewListResponse],
    summary="리뷰 목록 조회",
    description="리뷰 목록을 조회합니다. 검색, 필터링, 정렬, 페이지네이션을 지원합니다."
)
def get_reviews(
    book_id: Optional[int] = Query(None, description="도서 ID 필터"),
    user_id: Optional[int] = Query(None, description="작성자 ID 필터"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="최소 평점 필터"),
    sort: str = Query("created_at", description="정렬 기준 (created_at, rating, like_count)"),
    order: str = Query("desc", description="정렬 순서 (asc, desc)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """리뷰 목록 조회"""
    current_user_id = current_user.id if current_user else None

    reviews, total = ReviewService.get_reviews(
        db=db,
        current_user_id=current_user_id,
        book_id=book_id,
        user_id=user_id,
        min_rating=min_rating,
        sort=sort,
        order=order,
        page=page,
        size=size
    )

    # 응답 데이터 구성
    review_list = [ReviewResponse.model_validate(review) for review in reviews]
    total_pages = math.ceil(total / size) if total > 0 else 0

    return BaseResponse(
        is_success=True,
        message="Reviews retrieved successfully",
        payload=ReviewListResponse(
            content=review_list,
            page=page,
            size=size,
            total_elements=total,
            total_pages=total_pages,
            sort=f"{sort},{order}"
        )
    )


@router.get(
    "/{review_id}",
    response_model=BaseResponse[ReviewResponse],
    summary="리뷰 상세 조회",
    description="특정 리뷰의 상세 정보를 조회합니다."
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """리뷰 상세 조회"""
    current_user_id = current_user.id if current_user else None
    review = ReviewService.get_review(db, review_id, current_user_id)

    return BaseResponse(
        is_success=True,
        message="Review retrieved successfully",
        payload=ReviewResponse.model_validate(review)
    )


@router.patch(
    "/{review_id}",
    response_model=BaseResponse[ReviewResponse],
    summary="리뷰 수정",
    description="본인이 작성한 리뷰를 수정합니다."
)
def update_review(
    review_id: int,
    data: ReviewUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 수정 (본인만 가능)"""
    review = ReviewService.update_review(db, review_id, current_user.id, data)

    # 좋아요 정보 추가
    review = ReviewService.get_review(db, review_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Review updated successfully",
        payload=ReviewResponse.model_validate(review)
    )


@router.delete(
    "/{review_id}",
    response_model=BaseResponse[None],
    summary="리뷰 삭제",
    description="본인이 작성한 리뷰를 삭제합니다."
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 삭제 (본인만 가능)"""
    ReviewService.delete_review(db, review_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Review deleted successfully",
        payload=None
    )


@router.post(
    "/{review_id}/like",
    response_model=BaseResponse[LikeToggleResponse],
    summary="리뷰 좋아요 토글",
    description="리뷰에 좋아요를 추가하거나 취소합니다."
)
def toggle_like(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """리뷰 좋아요 토글"""
    is_liked, like_count = ReviewService.toggle_like(db, review_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Like toggled successfully",
        payload=LikeToggleResponse(is_liked=is_liked, like_count=like_count)
    )
