"""
Comments Router
댓글 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.domains.comments.schemas import (
    CommentCreateRequest,
    CommentUpdateRequest,
    CommentResponse,
    CommentListResponse,
    LikeToggleResponse
)
from app.domains.comments.service import CommentService
from app.domains.base import BaseResponse
from typing import Optional
import math


router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


@router.post(
    "",
    response_model=BaseResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="댓글 작성",
    description="리뷰에 댓글을 작성합니다. 대댓글도 지원합니다."
)
def create_comment(
    data: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """댓글 작성"""
    comment = CommentService.create_comment(db, current_user.id, data)

    # 응답 데이터 구성
    comment.like_count = 0
    comment.is_liked = False
    comment.user_name = current_user.name

    return BaseResponse(
        is_success=True,
        message="Comment created successfully",
        payload=CommentResponse.model_validate(comment)
    )


@router.get(
    "",
    response_model=BaseResponse[CommentListResponse],
    summary="댓글 목록 조회",
    description="댓글 목록을 조회합니다. 리뷰별, 사용자별 필터링을 지원합니다."
)
def get_comments(
    review_id: Optional[int] = Query(None, description="리뷰 ID 필터"),
    user_id: Optional[int] = Query(None, description="작성자 ID 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """댓글 목록 조회"""
    current_user_id = current_user.id if current_user else None

    comments, total = CommentService.get_comments(
        db=db,
        current_user_id=current_user_id,
        review_id=review_id,
        user_id=user_id,
        page=page,
        size=size
    )

    # 응답 데이터 구성
    comment_list = [CommentResponse.model_validate(comment) for comment in comments]
    total_pages = math.ceil(total / size) if total > 0 else 0

    return BaseResponse(
        is_success=True,
        message="Comments retrieved successfully",
        payload=CommentListResponse(
            content=comment_list,
            page=page,
            size=size,
            total_elements=total,
            total_pages=total_pages
        )
    )


@router.get(
    "/{comment_id}",
    response_model=BaseResponse[CommentResponse],
    summary="댓글 상세 조회",
    description="특정 댓글의 상세 정보를 조회합니다."
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """댓글 상세 조회"""
    current_user_id = current_user.id if current_user else None
    comment = CommentService.get_comment(db, comment_id, current_user_id)

    return BaseResponse(
        is_success=True,
        message="Comment retrieved successfully",
        payload=CommentResponse.model_validate(comment)
    )


@router.patch(
    "/{comment_id}",
    response_model=BaseResponse[CommentResponse],
    summary="댓글 수정",
    description="본인이 작성한 댓글을 수정합니다."
)
def update_comment(
    comment_id: int,
    data: CommentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """댓글 수정 (본인만 가능)"""
    comment = CommentService.update_comment(db, comment_id, current_user.id, data)

    # 좋아요 정보 추가
    comment = CommentService.get_comment(db, comment_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Comment updated successfully",
        payload=CommentResponse.model_validate(comment)
    )


@router.delete(
    "/{comment_id}",
    response_model=BaseResponse[None],
    summary="댓글 삭제",
    description="본인이 작성한 댓글을 삭제합니다."
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """댓글 삭제 (본인만 가능)"""
    CommentService.delete_comment(db, comment_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Comment deleted successfully",
        payload=None
    )


@router.post(
    "/{comment_id}/like",
    response_model=BaseResponse[LikeToggleResponse],
    summary="댓글 좋아요 토글",
    description="댓글에 좋아요를 추가하거나 취소합니다."
)
def toggle_like(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """댓글 좋아요 토글"""
    is_liked, like_count = CommentService.toggle_like(db, comment_id, current_user.id)

    return BaseResponse(
        is_success=True,
        message="Like toggled successfully",
        payload=LikeToggleResponse(is_liked=is_liked, like_count=like_count)
    )
