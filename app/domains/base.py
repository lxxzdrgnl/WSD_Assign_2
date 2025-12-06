"""
Base Schemas
공통 응답 스키마
"""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """기본 응답 스키마"""
    is_success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    payload: Optional[T] = Field(None, description="응답 데이터")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_success": True,
                "message": "Success",
                "payload": {}
            }
        }
    }
