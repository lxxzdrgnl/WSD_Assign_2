"""
Security Module
JWT 토큰 생성/검증 및 비밀번호 해싱
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
import os
from app.core.exceptions import UnauthorizedException, TokenExpiredException
from app.core.error_codes import ErrorCode

# JWT 설정 (환경 변수 또는 기본값)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password: str) -> str:
    """
    비밀번호를 bcrypt로 해싱
    bcrypt는 72 bytes 제한이 있으므로 자동으로 truncate

    Args:
        password: 평문 비밀번호

    Returns:
        해싱된 비밀번호
    """
    # bcrypt has a 72-byte password limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해싱된 비밀번호

    Returns:
        비밀번호 일치 여부
    """
    # bcrypt has a 72-byte password limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Access Token 생성

    Args:
        data: JWT payload 데이터 (user_id, email, role 등)
        expires_delta: 만료 시간 (기본값: 설정의 ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        생성된 JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Refresh Token 생성

    Args:
        data: JWT payload 데이터 (user_id)
        expires_delta: 만료 시간 (기본값: 설정의 REFRESH_TOKEN_EXPIRE_DAYS)

    Returns:
        생성된 JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰 디코딩 및 검증

    Args:
        token: JWT 토큰

    Returns:
        디코딩된 payload

    Raises:
        TokenExpiredException: 토큰 만료
        UnauthorizedException: 유효하지 않은 토큰
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException(
            message="토큰이 만료되었습니다. 다시 로그인해주세요."
        )
    except JWTError:
        raise UnauthorizedException(
            error_code=ErrorCode.INVALID_TOKEN,
            message="유효하지 않은 토큰입니다."
        )


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> None:
    """
    토큰 타입 검증

    Args:
        payload: 디코딩된 JWT payload
        expected_type: 기대하는 토큰 타입 ("access" 또는 "refresh")

    Raises:
        UnauthorizedException: 토큰 타입 불일치
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        raise UnauthorizedException(
            error_code=ErrorCode.INVALID_TOKEN,
            message=f"잘못된 토큰 타입입니다. {expected_type} 토큰이 필요합니다."
        )
