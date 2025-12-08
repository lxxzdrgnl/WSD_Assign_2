"""
Comments Service
댓글 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from app.models.comment import Comment, CommentLike
from app.models.review import Review
from app.models.user import User, UserRole
from app.domains.comments.schemas import CommentCreateRequest, CommentUpdateRequest
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from typing import Optional


class CommentService:
    """댓글 서비스"""

    @staticmethod
    def create_comment(db: Session, user_id: int, data: CommentCreateRequest) -> Comment:
        """
        댓글 작성

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            data: 댓글 데이터

        Returns:
            Comment: 생성된 댓글

        Raises:
            NotFoundException: 리뷰 또는 부모 댓글을 찾을 수 없음
        """
        # 리뷰 존재 확인
        review = db.query(Review).filter(Review.id == data.review_id).first()
        if not review:
            raise NotFoundException("REVIEW_NOT_FOUND", "Review not found")

        # 부모 댓글 존재 확인 (대댓글인 경우)
        if data.parent_id:
            parent = db.query(Comment).filter(Comment.id == data.parent_id).first()
            if not parent:
                raise NotFoundException("PARENT_COMMENT_NOT_FOUND", "Parent comment not found")

            # 부모 댓글이 같은 리뷰의 댓글인지 확인
            if parent.review_id != data.review_id:
                raise BadRequestException(
                    "INVALID_PARENT_COMMENT",
                    "Parent comment must belong to the same review"
                )

        # 댓글 생성
        comment = Comment(
            review_id=data.review_id,
            user_id=user_id,
            parent_comment_id=data.parent_id,
            content=data.content
        )

        try:
            db.add(comment)
            db.commit()
            db.refresh(comment)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("COMMENT_CREATE_FAILED", f"Failed to create comment: {str(e)}")

        return comment

    @staticmethod
    def get_comments(
        db: Session,
        current_user_id: Optional[int],
        review_id: Optional[int] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[list[Comment], int]:
        """
        댓글 목록 조회

        Args:
            db: 데이터베이스 세션
            current_user_id: 현재 사용자 ID (선택)
            review_id: 리뷰 ID 필터 (선택)
            user_id: 작성자 ID 필터 (선택)
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            tuple: (댓글 목록, 전체 개수)
        """
        query = db.query(Comment)

        # 필터링
        if review_id:
            query = query.filter(Comment.review_id == review_id)
        if user_id:
            query = query.filter(Comment.user_id == user_id)

        # 정렬 (최신순)
        query = query.order_by(desc(Comment.created_at))

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * size
        comments = query.offset(offset).limit(size).all()

        # 현재 사용자의 좋아요 여부 및 좋아요 수 추가
        for comment in comments:
            # 좋아요 수
            like_count = db.query(func.count(CommentLike.id)).filter(
                CommentLike.comment_id == comment.id
            ).scalar()
            comment.like_count = like_count or 0

            # 현재 사용자의 좋아요 여부
            if current_user_id:
                is_liked = db.query(CommentLike).filter(
                    CommentLike.comment_id == comment.id,
                    CommentLike.user_id == current_user_id
                ).first() is not None
                comment.is_liked = is_liked
            else:
                comment.is_liked = False

            # 작성자 이름 추가
            user = db.query(User).filter(User.id == comment.user_id).first()
            comment.user_name = user.name if user else "Unknown"

        return comments, total

    @staticmethod
    def get_comment(db: Session, comment_id: int, current_user_id: Optional[int]) -> Comment:
        """
        댓글 상세 조회

        Args:
            db: 데이터베이스 세션
            comment_id: 댓글 ID
            current_user_id: 현재 사용자 ID (선택)

        Returns:
            Comment: 댓글 객체

        Raises:
            NotFoundException: 댓글을 찾을 수 없음
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("COMMENT_NOT_FOUND", "Comment not found")

        # 좋아요 수
        like_count = db.query(func.count(CommentLike.id)).filter(
            CommentLike.comment_id == comment.id
        ).scalar()
        comment.like_count = like_count or 0

        # 현재 사용자의 좋아요 여부
        if current_user_id:
            is_liked = db.query(CommentLike).filter(
                CommentLike.comment_id == comment.id,
                CommentLike.user_id == current_user_id
            ).first() is not None
            comment.is_liked = is_liked
        else:
            comment.is_liked = False

        # 작성자 이름
        user = db.query(User).filter(User.id == comment.user_id).first()
        comment.user_name = user.name if user else "Unknown"

        return comment

    @staticmethod
    def update_comment(db: Session, comment_id: int, user_id: int, data: CommentUpdateRequest) -> Comment:
        """
        댓글 수정 (본인만 가능)

        Args:
            db: 데이터베이스 세션
            comment_id: 댓글 ID
            user_id: 사용자 ID
            data: 수정할 데이터

        Returns:
            Comment: 수정된 댓글

        Raises:
            NotFoundException: 댓글을 찾을 수 없음
            ForbiddenException: 본인의 댓글이 아님
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("COMMENT_NOT_FOUND", "Comment not found")

        # 권한 확인
        if comment.user_id != user_id:
            raise ForbiddenException("FORBIDDEN", "You can only update your own comments")

        # 내용 업데이트
        comment.content = data.content

        try:
            db.commit()
            db.refresh(comment)
        except IntegrityError as e:
            db.rollback()
            raise BadRequestException("UPDATE_FAILED", f"Failed to update comment: {str(e)}")

        return comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int, current_user: User) -> None:
        """
        댓글 삭제 (본인 또는 관리자 가능)

        Args:
            db: 데이터베이스 세션
            comment_id: 댓글 ID
            current_user: 현재 사용자 객체

        Raises:
            NotFoundException: 댓글을 찾을 수 없음
            ForbiddenException: 본인의 댓글이 아니고 관리자도 아님
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("COMMENT_NOT_FOUND", "Comment not found")

        # 권한 확인 (본인 또는 관리자)
        if comment.user_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise ForbiddenException("FORBIDDEN", "You can only delete your own comments")

        # CASCADE로 관련 데이터 자동 삭제 (comment_likes, 자식 댓글)
        db.delete(comment)
        db.commit()

    @staticmethod
    def toggle_like(db: Session, comment_id: int, user_id: int) -> tuple[bool, int]:
        """
        댓글 좋아요 토글

        Args:
            db: 데이터베이스 세션
            comment_id: 댓글 ID
            user_id: 사용자 ID

        Returns:
            tuple: (좋아요 상태, 총 좋아요 수)

        Raises:
            NotFoundException: 댓글을 찾을 수 없음
        """
        # 댓글 존재 확인
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("COMMENT_NOT_FOUND", "Comment not found")

        # 기존 좋아요 확인
        existing_like = db.query(CommentLike).filter(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == user_id
        ).first()

        is_liked = False

        if existing_like:
            # 좋아요 취소
            db.delete(existing_like)
        else:
            # 좋아요 추가
            new_like = CommentLike(comment_id=comment_id, user_id=user_id)
            db.add(new_like)
            is_liked = True

        db.commit()

        # 좋아요 수 조회
        like_count = db.query(func.count(CommentLike.id)).filter(
            CommentLike.comment_id == comment_id
        ).scalar()

        return is_liked, like_count or 0
