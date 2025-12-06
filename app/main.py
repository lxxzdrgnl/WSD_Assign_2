"""
FastAPI Application Entry Point
도서 구매 시스템 API 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.middleware.logging import logging_middleware
from app.middleware.error_handler import add_error_handlers
from app.domains.health.router import router as health_router
from app.domains.auth.router import router as auth_router
from app.domains.users.router import router as users_router
from app.domains.books.router import router as books_router
from app.domains.reviews.router import router as reviews_router
from app.domains.comments.router import router as comments_router
from app.domains.favorites.router import router as favorites_router
from app.domains.cart.router import router as cart_router
from app.domains.orders.router import router as orders_router
from app.domains.library.router import router as library_router
from app.domains.admin.router import router as admin_router
from app.domains.coupons.router import router as coupons_router

# FastAPI 앱 생성
app = FastAPI(
    title="Bookstore API",
    description="온라인 도서 구매 시스템 RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 레이트 리미터 설정
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# 로깅 미드웨어 추가
app.middleware("http")(logging_middleware)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들러 등록
add_error_handlers(app)

# 라우터 등록
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router, tags=["Auth"])
app.include_router(users_router, tags=["Users"])
app.include_router(books_router, tags=["Books"])
app.include_router(reviews_router, tags=["Reviews"])
app.include_router(comments_router, tags=["Comments"])
app.include_router(favorites_router, tags=["Favorites"])
app.include_router(cart_router, tags=["Cart"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(library_router, tags=["Library"])
app.include_router(coupons_router, tags=["Coupons"])
app.include_router(admin_router, tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 Bookstore API Server Starting...")
    print("📚 Total Endpoints: 41")
    print("📖 Swagger Docs: http://localhost:8000/docs")
    print("🔧 ReDoc: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("👋 Bookstore API Server Shutting Down...")


@app.get("/", include_in_schema=False)
async def root():
    """루트 엔드포인트"""
    return JSONResponse({
        "message": "Welcome to Bookstore API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    })
