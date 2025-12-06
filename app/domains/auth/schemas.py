"""
Auth Domain Schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from typing import Literal
import re


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    birth_date: date
    gender: Literal["MALE", "FEMALE"]
    address: str = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        if not re.search(r"[@$!%*?&#]", v):
            raise ValueError("Password must contain special char")
        return v


class SignupResponse(BaseModel):
    user_id: int
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
