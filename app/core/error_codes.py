"""
Standard Error Codes
표준 에러 코드 정의 (최소 10종 이상)
"""
from enum import Enum


class ErrorCode(str, Enum):
    """에러 코드 열거형"""

    # 400 Bad Request
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INVALID_QUERY_PARAM = "INVALID_QUERY_PARAM"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"

    # 401 Unauthorized
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_MISSING = "TOKEN_MISSING"

    # 403 Forbidden
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    NOT_RESOURCE_OWNER = "NOT_RESOURCE_OWNER"

    # 404 Not Found
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    BOOK_NOT_FOUND = "BOOK_NOT_FOUND"
    REVIEW_NOT_FOUND = "REVIEW_NOT_FOUND"
    COMMENT_NOT_FOUND = "COMMENT_NOT_FOUND"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    CART_ITEM_NOT_FOUND = "CART_ITEM_NOT_FOUND"
    FAVORITE_NOT_FOUND = "FAVORITE_NOT_FOUND"
    COUPON_NOT_FOUND = "COUPON_NOT_FOUND"

    # 409 Conflict
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    ISBN_ALREADY_EXISTS = "ISBN_ALREADY_EXISTS"
    ALREADY_LIKED = "ALREADY_LIKED"
    ALREADY_IN_CART = "ALREADY_IN_CART"
    ALREADY_IN_FAVORITES = "ALREADY_IN_FAVORITES"
    STATE_CONFLICT = "STATE_CONFLICT"

    # 422 Unprocessable Entity
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    ORDER_NOT_PURCHASABLE = "ORDER_NOT_PURCHASABLE"
    REVIEW_REQUIRES_PURCHASE = "REVIEW_REQUIRES_PURCHASE"
    COUPON_NOT_APPLICABLE = "COUPON_NOT_APPLICABLE"
    COUPON_EXPIRED = "COUPON_EXPIRED"
    COUPON_ALREADY_USED = "COUPON_ALREADY_USED"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    INVALID_ORDER_STATUS = "INVALID_ORDER_STATUS"

    # 429 Too Many Requests
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 500 Internal Server Error
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


# 에러 메시지 매핑
ERROR_MESSAGES = {
    # 400
    ErrorCode.BAD_REQUEST: "잘못된 요청입니다.",
    ErrorCode.VALIDATION_FAILED: "입력값 검증에 실패했습니다.",
    ErrorCode.INVALID_QUERY_PARAM: "잘못된 쿼리 파라미터입니다.",
    ErrorCode.INVALID_DATE_RANGE: "잘못된 날짜 범위입니다.",

    # 401
    ErrorCode.UNAUTHORIZED: "인증이 필요합니다.",
    ErrorCode.TOKEN_EXPIRED: "토큰이 만료되었습니다.",
    ErrorCode.INVALID_TOKEN: "유효하지 않은 토큰입니다.",
    ErrorCode.INVALID_CREDENTIALS: "이메일 또는 비밀번호가 올바르지 않습니다.",
    ErrorCode.TOKEN_MISSING: "인증 토큰이 없습니다.",

    # 403
    ErrorCode.FORBIDDEN: "접근 권한이 없습니다.",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "권한이 부족합니다.",
    ErrorCode.NOT_RESOURCE_OWNER: "해당 리소스의 소유자가 아닙니다.",

    # 404
    ErrorCode.RESOURCE_NOT_FOUND: "요청한 리소스를 찾을 수 없습니다.",
    ErrorCode.USER_NOT_FOUND: "사용자를 찾을 수 없습니다.",
    ErrorCode.BOOK_NOT_FOUND: "도서를 찾을 수 없습니다.",
    ErrorCode.REVIEW_NOT_FOUND: "리뷰를 찾을 수 없습니다.",
    ErrorCode.COMMENT_NOT_FOUND: "댓글을 찾을 수 없습니다.",
    ErrorCode.ORDER_NOT_FOUND: "주문을 찾을 수 없습니다.",
    ErrorCode.CART_ITEM_NOT_FOUND: "장바구니 항목을 찾을 수 없습니다.",
    ErrorCode.FAVORITE_NOT_FOUND: "위시리스트 항목을 찾을 수 없습니다.",
    ErrorCode.COUPON_NOT_FOUND: "쿠폰을 찾을 수 없습니다.",

    # 409
    ErrorCode.DUPLICATE_RESOURCE: "이미 존재하는 리소스입니다.",
    ErrorCode.EMAIL_ALREADY_EXISTS: "이미 사용 중인 이메일입니다.",
    ErrorCode.ISBN_ALREADY_EXISTS: "이미 등록된 ISBN입니다.",
    ErrorCode.ALREADY_LIKED: "이미 좋아요를 눌렀습니다.",
    ErrorCode.ALREADY_IN_CART: "이미 장바구니에 있는 상품입니다.",
    ErrorCode.ALREADY_IN_FAVORITES: "이미 위시리스트에 있는 상품입니다.",
    ErrorCode.STATE_CONFLICT: "리소스 상태 충돌이 발생했습니다.",

    # 422
    ErrorCode.UNPROCESSABLE_ENTITY: "처리할 수 없는 요청입니다.",
    ErrorCode.ORDER_NOT_PURCHASABLE: "구매할 수 없는 주문입니다.",
    ErrorCode.REVIEW_REQUIRES_PURCHASE: "구매한 도서만 리뷰를 작성할 수 있습니다.",
    ErrorCode.COUPON_NOT_APPLICABLE: "적용할 수 없는 쿠폰입니다.",
    ErrorCode.COUPON_EXPIRED: "만료된 쿠폰입니다.",
    ErrorCode.COUPON_ALREADY_USED: "이미 사용한 쿠폰입니다.",
    ErrorCode.INSUFFICIENT_STOCK: "재고가 부족합니다.",
    ErrorCode.INVALID_ORDER_STATUS: "유효하지 않은 주문 상태입니다.",

    # 429
    ErrorCode.TOO_MANY_REQUESTS: "너무 많은 요청을 보냈습니다.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "요청 한도를 초과했습니다.",

    # 500
    ErrorCode.INTERNAL_SERVER_ERROR: "서버 내부 오류가 발생했습니다.",
    ErrorCode.DATABASE_ERROR: "데이터베이스 오류가 발생했습니다.",
    ErrorCode.UNKNOWN_ERROR: "알 수 없는 오류가 발생했습니다.",
    ErrorCode.EXTERNAL_SERVICE_ERROR: "외부 서비스 오류가 발생했습니다.",
}
