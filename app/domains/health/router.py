"""
Health Check Router
서버 상태 확인 엔드포인트
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="헬스체크",
    description="서버 상태를 확인합니다. 인증 없이 접근 가능합니다."
)
def health_check():
    """헬스체크 API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "Bookstore API",
        "version": "1.0.0"
    }
