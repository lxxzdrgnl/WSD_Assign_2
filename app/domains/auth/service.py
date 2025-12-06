"""
Auth Domain Service
"""
from sqlalchemy.orm import Session
from app.models import User, RefreshToken, UserRole
from app.domains.auth import schemas
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, verify_token_type
)
from app.core.exceptions import (
    EmailAlreadyExistsException, InvalidCredentialsException, UnauthorizedException
)
from app.core.error_codes import ErrorCode
from app.config import settings


def signup(db: Session, request: schemas.SignupRequest) -> schemas.SignupResponse:
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise EmailAlreadyExistsException(message=f"Email {request.email} already exists")
    
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email, password=hashed_password, name=request.name,
        birth_date=request.birth_date, gender=request.gender,
        address=request.address, role=UserRole.CUSTOMER
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schemas.SignupResponse(user_id=new_user.id, created_at=new_user.created_at)


def login(db: Session, request: schemas.LoginRequest) -> schemas.TokenResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise InvalidCredentialsException(message="Invalid credentials")
    
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token({"user_id": user.id})
    
    refresh_token = RefreshToken(user_id=user.id, token=refresh_token_str)
    db.add(refresh_token)
    db.commit()
    
    return schemas.TokenResponse(
        access_token=access_token, refresh_token=refresh_token_str,
        token_type="Bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def refresh_access_token(db: Session, request: schemas.RefreshTokenRequest) -> schemas.TokenResponse:
    payload = decode_token(request.refresh_token)
    verify_token_type(payload, "refresh")
    user_id = payload.get("user_id")
    if not user_id:
        raise UnauthorizedException(error_code=ErrorCode.INVALID_TOKEN)
    
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token, RefreshToken.user_id == user_id
    ).first()
    if not db_token:
        raise UnauthorizedException(error_code=ErrorCode.INVALID_TOKEN)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException(error_code=ErrorCode.USER_NOT_FOUND)
    
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    
    return schemas.TokenResponse(
        access_token=access_token, refresh_token=request.refresh_token,
        token_type="Bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def logout(db: Session, request: schemas.LogoutRequest) -> None:
    payload = decode_token(request.refresh_token)
    verify_token_type(payload, "refresh")
    db_token = db.query(RefreshToken).filter(RefreshToken.token == request.refresh_token).first()
    if db_token:
        db.delete(db_token)
        db.commit()
