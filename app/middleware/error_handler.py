"""
Global Error Handler Middleware
전역 예외 처리 미들웨어
"""
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime
from slowapi.errors import RateLimitExceeded
from app.core.exceptions import BaseAPIException
from app.core.error_codes import ErrorCode
import traceback


def add_error_handlers(app: FastAPI):
    """FastAPI 앱에 에러 핸들러 등록"""

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 429,
                "code": "TOO_MANY_REQUESTS",
                "message": "요청 횟수가 너무 많습니다. 잠시 후 다시 시도해주세요.",
                "details": {"retry_after": exc.retry_after}
            }
        )

    @app.exception_handler(BaseAPIException)
    async def custom_exception_handler(request: Request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": exc.status_code,
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 400,
                "code": "VALIDATION_FAILED",
                "message": "입력값이 올바르지 않습니다.",
                "details": {"errors": [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # 스택 트레이스 로깅
        traceback.print_exc()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 500,
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버에 오류가 발생했습니다.",
                "details": {}
            }
        )

