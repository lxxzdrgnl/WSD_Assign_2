"""
Base Schemas
공통 응답 스키마 및 페이지네이션
"""
from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """기본 API 응답 형식"""

    isSuccess: bool = Field(..., description="요청 처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    payload: Optional[T] = Field(None, description="응답 데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "isSuccess": True,
                "message": "요청이 성공적으로 처리되었습니다.",
                "payload": {}
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답 형식"""

    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시각")
    path: str = Field(..., description="요청 경로")
    status: int = Field(..., description="HTTP 상태 코드")
    code: str = Field(..., description="내부 에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: Optional[dict] = Field(None, description="에러 상세 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-05T12:00:00Z",
                "path": "/api/v1/books/999",
                "status": 404,
                "code": "BOOK_NOT_FOUND",
                "message": "도서를 찾을 수 없습니다.",
                "details": {"bookId": 999}
            }
        }


class PaginationParams(BaseModel):
    """페이지네이션 파라미터"""

    page: int = Field(1, ge=1, description="페이지 번호 (1부터 시작)")
    size: int = Field(10, ge=1, le=100, description="페이지 크기 (최대 100)")
    sort: Optional[str] = Field("created_at,desc", description="정렬 기준 (필드명,asc|desc)")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 10,
                "sort": "created_at,desc"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답"""

    content: List[T] = Field(..., description="데이터 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    totalElements: int = Field(..., description="전체 항목 수")
    totalPages: int = Field(..., description="전체 페이지 수")
    sort: Optional[str] = Field(None, description="정렬 기준")

    class Config:
        json_schema_extra = {
            "example": {
                "content": [],
                "page": 1,
                "size": 10,
                "totalElements": 100,
                "totalPages": 10,
                "sort": "created_at,desc"
            }
        }


class SuccessResponse(BaseResponse[None]):
    """성공 응답 (payload 없음)"""

    isSuccess: bool = True
    payload: None = None

    class Config:
        json_schema_extra = {
            "example": {
                "isSuccess": True,
                "message": "작업이 성공적으로 완료되었습니다.",
                "payload": None
            }
        }
