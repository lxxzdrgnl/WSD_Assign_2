"""
Auth Domain Router
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.auth import schemas, service
from app.domains.base import BaseResponse, SuccessResponse
from app.core.limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=BaseResponse[schemas.SignupResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def signup(data: schemas.SignupRequest, request: Request, db: Session = Depends(get_db)):
    result = service.signup(db, data)
    return BaseResponse(is_success=True, message="회원가입에 성공했습니다.", payload=result)


@router.post("/login", response_model=BaseResponse[schemas.TokenResponse])
@limiter.limit("10/minute")
def login(data: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    result = service.login(db, data)
    return BaseResponse(is_success=True, message="로그인에 성공했습니다.", payload=result)


@router.post("/refresh", response_model=BaseResponse[schemas.TokenResponse])
@limiter.limit("60/minute")
def refresh_token(data: schemas.RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    result = service.refresh_access_token(db, data)
    return BaseResponse(is_success=True, message="토큰이 갱신되었습니다.", payload=result)


@router.post("/logout", response_model=SuccessResponse)
@limiter.limit("60/minute")
def logout(data: schemas.LogoutRequest, request: Request, db: Session = Depends(get_db)):
    service.logout(db, data)
    return SuccessResponse(message="로그아웃에 성공했습니다.")
