"""
Auth Domain Router
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.auth import schemas, service
from app.schemas.base import BaseResponse, SuccessResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/signup", response_model=BaseResponse[schemas.SignupResponse], status_code=status.HTTP_201_CREATED)
def signup(request: schemas.SignupRequest, db: Session = Depends(get_db)):
    result = service.signup(db, request)
    return BaseResponse(isSuccess=True, message="Signup successful", payload=result)


@router.post("/login", response_model=BaseResponse[schemas.TokenResponse])
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    result = service.login(db, request)
    return BaseResponse(isSuccess=True, message="Login successful", payload=result)


@router.post("/refresh", response_model=BaseResponse[schemas.TokenResponse])
def refresh_token(request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    result = service.refresh_access_token(db, request)
    return BaseResponse(isSuccess=True, message="Token refreshed", payload=result)


@router.post("/logout", response_model=SuccessResponse)
def logout(request: schemas.LogoutRequest, db: Session = Depends(get_db)):
    service.logout(db, request)
    return SuccessResponse(message="Logout successful")
