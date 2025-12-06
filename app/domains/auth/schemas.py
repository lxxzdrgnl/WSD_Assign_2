"""
Auth Domain Schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from typing import Literal
import re


class SignupRequest(BaseModel):
    email: EmailStr = Field(example="user@example.com")
    password: str = Field(min_length=8, max_length=100, example="Test1234!")
    name: str = Field(min_length=1, max_length=100, example="John Doe")
    birth_date: date = Field(example="1990-01-01")
    gender: Literal["MALE", "FEMALE"] = Field(example="MALE")
    address: str = Field(None, max_length=255, example="123 Main St, Seoul")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "Test1234!",
                    "name": "John Doe",
                    "birth_date": "1990-01-01",
                    "gender": "MALE",
                    "address": "123 Main St, Seoul"
                }
            ]
        }
    }

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
    email: EmailStr = Field(example="seller1@bookstore.com")
    password: str = Field(example="seller1123!")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "seller1@bookstore.com",
                    "password": "seller1123!"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
