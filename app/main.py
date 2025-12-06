"""
FastAPI Main Application
애플리케이션 진입점
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import Base, engine
from app.middleware.error_handler import error_handler_middleware, validation_exception_handler

# 라우터 import
from app.domains.auth.router import router as auth_router
from app.domains.health.router import router as health_router

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="온라인 도서 구매 시스템 RESTful API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들러 등록
app.middleware("http")(error_handler_middleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 데이터베이스 테이블 생성
@app.on_event("startup")
def startup_event():
    """애플리케이션 시작 시 DB 테이블 생성"""
    Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(health_router)
app.include_router(auth_router)

# Root 엔드포인트
@app.get("/", tags=["Root"])
def root():
    """API 루트"""
    return {
        "message": "Bookstore API Server",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
