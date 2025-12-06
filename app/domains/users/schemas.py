"""
Users Schemas
사용자 프로필 관련 요청/응답 스키마
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional
from app.models.user import UserRole, Gender


class UserResponse(BaseModel):
    """사용자 프로필 응답"""
    id: int = Field(..., description="사용자 ID")
    role: UserRole = Field(..., description="사용자 역할")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="이름")
    birth_date: date = Field(..., description="생년월일")
    gender: Gender = Field(..., description="성별")
    address: Optional[str] = Field(None, description="주소")
    created_at: datetime = Field(..., description="계정 생성일")
    updated_at: datetime = Field(..., description="최종 수정일")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 11,
                "role": "CUSTOMER",
                "email": "customer1@example.com",
                "name": "김민준",
                "birth_date": "1990-02-02",
                "gender": "FEMALE",
                "address": "서울특별시 서초구",
                "created_at": "2025-12-06T10:00:00",
                "updated_at": "2025-12-06T10:00:00"
            }
        }
    }


class UserUpdateRequest(BaseModel):
    """사용자 프로필 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="이름")
    birth_date: Optional[date] = Field(None, description="생년월일")
    gender: Optional[Gender] = Field(None, description="성별")
    address: Optional[str] = Field(None, max_length=255, description="주소")
    password: Optional[str] = Field(None, min_length=8, max_length=72, description="새 비밀번호 (8자 이상)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """비밀번호 강도 검증"""
        if v is None:
            return v

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 72:
            raise ValueError('Password must be at most 72 characters long (bcrypt limitation)')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '@$!%*?&' for c in v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "김철수",
                "birth_date": "1995-05-15",
                "gender": "MALE",
                "address": "서울시 서초구 서초대로 123",
                "password": "NewPass1234!"
            }
        }
    }
