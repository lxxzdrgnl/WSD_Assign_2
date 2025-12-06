"""
FastAPI Dependencies
인증 및 권한 의존성 함수
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, UserRole
from app.core.security import decode_token, verify_token_type
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    InsufficientPermissionsException,
    UserNotFoundException
)
from app.core.error_codes import ErrorCode

# HTTP Bearer 토큰 스키마
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 가져오기

    Args:
        credentials: HTTP Authorization Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        현재 사용자 객체

    Raises:
        UnauthorizedException: 토큰 없음 또는 유효하지 않음
        UserNotFoundException: 사용자를 찾을 수 없음
    """
    token = credentials.credentials

    # 토큰 디코딩 및 검증
    payload = decode_token(token)
    verify_token_type(payload, "access")

    # 사용자 ID 추출
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise UnauthorizedException(
            error_code=ErrorCode.INVALID_TOKEN,
            message="토큰에 사용자 정보가 없습니다."
        )

    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundException(
            message="사용자를 찾을 수 없습니다.",
            details={"user_id": user_id}
        )

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적 인증 (로그인하지 않아도 되는 경우)

    Args:
        credentials: HTTP Authorization Bearer 토큰 (Optional)
        db: 데이터베이스 세션

    Returns:
        현재 사용자 객체 또는 None
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


def require_role(allowed_roles: List[UserRole]):
    """
    특정 역할(Role)을 가진 사용자만 접근 가능하도록 하는 의존성

    Args:
        allowed_roles: 허용된 역할 리스트

    Returns:
        의존성 함수

    Example:
        @router.get("/admin/users", dependencies=[Depends(require_role([UserRole.ADMIN]))])
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsException(
                message=f"이 작업은 {', '.join([role.value for role in allowed_roles])} 권한이 필요합니다.",
                details={
                    "required_roles": [role.value for role in allowed_roles],
                    "user_role": current_user.role.value
                }
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    관리자 권한 필요

    Args:
        current_user: 현재 사용자

    Returns:
        현재 사용자 (관리자인 경우)

    Raises:
        InsufficientPermissionsException: 관리자가 아닌 경우
    """
    if current_user.role != UserRole.ADMIN:
        raise InsufficientPermissionsException(
            message="관리자 권한이 필요합니다.",
            details={"user_role": current_user.role.value}
        )
    return current_user


def require_seller(current_user: User = Depends(get_current_user)) -> User:
    """
    판매자 권한 필요 (판매자 또는 관리자)

    Args:
        current_user: 현재 사용자

    Returns:
        현재 사용자 (판매자 또는 관리자인 경우)

    Raises:
        InsufficientPermissionsException: 판매자가 아닌 경우
    """
    if current_user.role not in [UserRole.SELLER, UserRole.ADMIN]:
        raise InsufficientPermissionsException(
            message="판매자 권한이 필요합니다.",
            details={"user_role": current_user.role.value}
        )
    return current_user


def verify_resource_owner(resource_user_id: int, current_user: User) -> None:
    """
    리소스 소유자 검증 (본인 또는 관리자만 접근 가능)

    Args:
        resource_user_id: 리소스 소유자 ID
        current_user: 현재 사용자

    Raises:
        ForbiddenException: 본인이 아니고 관리자도 아닌 경우
    """
    if current_user.id != resource_user_id and current_user.role != UserRole.ADMIN:
        raise ForbiddenException(
            error_code=ErrorCode.NOT_RESOURCE_OWNER,
            message="해당 리소스에 접근할 권한이 없습니다."
        )
