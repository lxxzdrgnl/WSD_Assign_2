"""
Global Error Handler Middleware
전역 예외 처리 미들웨어
"""
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime
from app.core.exceptions import BaseAPIException
from app.core.error_codes import ErrorCode
import traceback


def add_error_handlers(app: FastAPI):
    """FastAPI 앱에 에러 핸들러 등록"""

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
                "message": "Validation failed",
                "details": {"errors": [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 500,
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
                "details": {"error": str(exc)}
            }
        )


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
    except ValidationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 400,
                "code": ErrorCode.VALIDATION_FAILED,
                "message": "Validation failed",
                "details": {"errors": [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}
            }
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 400,
                "code": ErrorCode.VALIDATION_FAILED,
                "message": str(exc),
                "details": {}
            }
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": str(request.url.path),
                "status": 500,
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
                "details": {"error": str(exc), "type": type(exc).__name__}
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
