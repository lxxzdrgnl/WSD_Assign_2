"""
Users Router
사용자 프로필 관련 엔드포인트
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.domains.users.schemas import UserResponse, UserUpdateRequest
from app.domains.users.service import UserService
from app.schemas.base import BaseResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="내 프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
    operation_id="users.list"
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 프로필 조회

    - **인증 필요**: JWT Access Token
    - **권한**: 모든 로그인 사용자
    """
    user = UserService.get_profile(db, current_user.id)

    return BaseResponse(
        isSuccess=True,
        message="Profile retrieved successfully",
        payload=UserResponse.model_validate(user)
    )


@router.patch(
    "/me",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다. 수정하려는 필드만 전송하면 됩니다.",
    operation_id="users.update"
)
def update_my_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    프로필 수정

    - **인증 필요**: JWT Access Token
    - **권한**: 모든 로그인 사용자
    - **수정 가능 필드**: name, birth_date, gender, address, password
    - **비밀번호 변경 시**: 8자 이상, 대소문자+숫자+특수문자 포함 필수
    """
    user = UserService.update_profile(db, current_user.id, data)

    return BaseResponse(
        isSuccess=True,
        message="Profile updated successfully",
        payload=UserResponse.model_validate(user)
    )


@router.delete(
    "/me",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="계정 삭제",
    description="현재 로그인한 사용자의 계정을 삭제합니다. 관련된 모든 데이터(리뷰, 댓글, 좋아요 등)가 함께 삭제됩니다.",
    operation_id="users.delete"
)
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    계정 삭제

    - **인증 필요**: JWT Access Token
    - **권한**: 모든 로그인 사용자
    - **주의**: 이 작업은 되돌릴 수 없습니다.
    - **함께 삭제되는 데이터**:
        - Refresh Tokens
        - 작성한 리뷰 및 댓글
        - 좋아요 기록
        - 위시리스트 및 장바구니
        - 쿠폰 발급 기록
        - 도서 조회 기록
    """
    UserService.delete_account(db, current_user.id)

    return BaseResponse(
        isSuccess=True,
        message="Account deleted successfully",
        payload=None
    )
