"""
Custom Exceptions
커스텀 예외 클래스 정의
"""
from typing import Any, Dict, Optional
from app.core.error_codes import ErrorCode, ERROR_MESSAGES


class BaseAPIException(Exception):
    """Base exception for all API errors"""

    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message or ERROR_MESSAGES.get(error_code, "An error occurred")
        self.details = details or {}
        super().__init__(self.message)


# 400 Bad Request
class BadRequestException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.BAD_REQUEST,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(400, error_code, message, details)


class ValidationException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(400, ErrorCode.VALIDATION_FAILED, message, details)


# 401 Unauthorized
class UnauthorizedException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.UNAUTHORIZED,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(401, error_code, message, details)


class TokenExpiredException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(401, ErrorCode.TOKEN_EXPIRED, message, details)


class InvalidCredentialsException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(401, ErrorCode.INVALID_CREDENTIALS, message, details)


# 403 Forbidden
class ForbiddenException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(403, error_code, message, details)


class InsufficientPermissionsException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(403, ErrorCode.INSUFFICIENT_PERMISSIONS, message, details)


# 404 Not Found
class NotFoundException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(404, error_code, message, details)


class UserNotFoundException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(404, ErrorCode.USER_NOT_FOUND, message, details)


class BookNotFoundException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(404, ErrorCode.BOOK_NOT_FOUND, message, details)


class ReviewNotFoundException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(404, ErrorCode.REVIEW_NOT_FOUND, message, details)


class OrderNotFoundException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(404, ErrorCode.ORDER_NOT_FOUND, message, details)


# 409 Conflict
class ConflictException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.DUPLICATE_RESOURCE,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(409, error_code, message, details)


class EmailAlreadyExistsException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(409, ErrorCode.EMAIL_ALREADY_EXISTS, message, details)


# 422 Unprocessable Entity
class UnprocessableEntityException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.UNPROCESSABLE_ENTITY,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(422, error_code, message, details)


class ReviewRequiresPurchaseException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(422, ErrorCode.REVIEW_REQUIRES_PURCHASE, message, details)


# 500 Internal Server Error
class InternalServerException(BaseAPIException):
    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(500, error_code, message, details)


class DatabaseException(BaseAPIException):
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(500, ErrorCode.DATABASE_ERROR, message, details)
