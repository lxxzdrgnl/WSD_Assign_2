"""
Global Error Handler Middleware
전역 예외 처리 미들웨어
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from app.core.exceptions import BaseAPIException
from app.core.error_codes import ErrorCode

async def error_handler_middleware(request: Request, call_next):
    """에러 핸들러 미들웨어"""
    try:
        response = await call_next(request)
        return response
    except BaseAPIException as exc:
        # 커스텀 예외 처리
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
    except Exception as exc:
        # 예상치 못한 에러
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 500,
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "서버 내부 오류가 발생했습니다.",
                "details": {"error": str(exc)}
            }
        )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 검증 오류 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "status": 400,
            "code": ErrorCode.VALIDATION_FAILED,
            "message": "입력값 검증에 실패했습니다.",
            "details": {"errors": exc.errors()}
        }
    )
