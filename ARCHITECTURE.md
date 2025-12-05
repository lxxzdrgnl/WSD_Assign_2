# FastAPI 도메인 기반 아키텍처 (Domain-Driven Design)

## 개선된 프로젝트 구조

```
WSD_assignment_2/
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI 애플리케이션 진입점
│   ├── config.py                       # 환경 설정 (DB, JWT 등)
│   ├── database.py                     # DB 연결 및 세션 관리
│   │
│   ├── models/                         # SQLAlchemy ORM 모델 (공통)
│   │   ├── __init__.py
│   │   ├── user.py                    # users, refresh_tokens
│   │   ├── book.py                    # books, books_view
│   │   ├── review.py                  # reviews, review_likes, review_like_counts
│   │   ├── comment.py                 # comments, comment_likes
│   │   ├── favorite.py                # favorites
│   │   ├── cart.py                    # carts
│   │   ├── order.py                   # orders, order_items
│   │   └── coupon.py                  # coupons, user_coupons
│   │
│   ├── schemas/                        # Pydantic 공통 스키마
│   │   ├── __init__.py
│   │   └── base.py                    # BaseResponse, PaginatedResponse, ErrorResponse
│   │
│   ├── core/                           # 핵심 유틸리티 (공통)
│   │   ├── __init__.py
│   │   ├── security.py                # JWT, 비밀번호 해싱
│   │   ├── dependencies.py            # FastAPI 의존성 (인증, 권한)
│   │   ├── exceptions.py              # 커스텀 예외
│   │   └── error_codes.py             # 표준 에러 코드
│   │
│   ├── middleware/                     # 미들웨어 (공통)
│   │   ├── __init__.py
│   │   ├── logging.py                 # 요청/응답 로깅
│   │   ├── error_handler.py           # 전역 에러 핸들러
│   │   └── cors.py                    # CORS 설정
│   │
│   └── domains/                        # 도메인별 모듈 (★ 핵심)
│       │
│       ├── auth/                       # 인증 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 라우터 (signup, login, logout, refresh)
│       │   ├── schemas.py             # 요청/응답 스키마
│       │   └── service.py             # 비즈니스 로직
│       │
│       ├── users/                      # 사용자 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 프로필 조회/수정/삭제
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── books/                      # 도서 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 도서 CRUD, 검색/정렬/페이지네이션
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── reviews/                    # 리뷰 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 리뷰 CRUD + 좋아요
│       │   ├── schemas.py
│       │   └── service.py             # 리뷰 좋아요 캐싱 로직
│       │
│       ├── comments/                   # 댓글 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 댓글 CRUD + 좋아요
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── favorites/                  # 위시리스트 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 위시리스트 추가/조회/삭제
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── cart/                       # 장바구니 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 장바구니 CRUD
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── orders/                     # 주문 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 주문 생성/조회/취소
│       │   ├── schemas.py
│       │   └── service.py             # 쿠폰 적용 로직
│       │
│       ├── coupons/                    # 쿠폰 도메인 (관리자)
│       │   ├── __init__.py
│       │   ├── router.py              # 쿠폰 생성/관리
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── admin/                      # 관리자 도메인
│       │   ├── __init__.py
│       │   ├── router.py              # 사용자 관리, 통계, 주문 상태 변경
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       └── health/                     # 헬스체크
│           ├── __init__.py
│           └── router.py              # 헬스체크 엔드포인트
│
├── alembic/                            # DB 마이그레이션
│   ├── versions/
│   └── env.py
│
├── scripts/                            # 스크립트
│   ├── seed_data.py                   # 초기 데이터 (200+건)
│   └── init_db.py                     # DB 초기화
│
├── tests/                              # 테스트 (20+개)
│   ├── __init__.py
│   ├── conftest.py                    # 테스트 설정
│   ├── test_auth.py
│   ├── test_books.py
│   ├── test_reviews.py
│   ├── test_orders.py
│   └── test_admin.py
│
├── docs/                               # 문서
│   ├── api-design.md
│   ├── db-schema.md
│   └── deployment.md
│
├── postman/                            # Postman 컬렉션
│   └── bookstore_api.postman_collection.json
│
├── .env.example
├── .gitignore
├── requirements.txt
├── alembic.ini
├── README.md
├── ARCHITECTURE.md                     # 이 문서
└── claude.md                           # 구현 계획서
```

---

## 도메인 기반 설계의 장점

### 1. **명확한 책임 분리**
각 도메인(auth, users, books 등)이 독립적인 모듈로 구성되어 있어, 해당 도메인의 로직을 한 곳에서 관리할 수 있습니다.

### 2. **확장성**
- 새로운 기능 추가 시, 해당 도메인 폴더에만 작업하면 됨
- 예: 새로운 "notifications" 도메인 추가 → `app/domains/notifications/` 생성

### 3. **테스트 용이성**
- 도메인별로 독립적인 테스트 작성 가능
- Mock 객체를 사용한 단위 테스트가 용이

### 4. **코드 가독성**
- 파일 경로만 봐도 어떤 기능인지 명확히 알 수 있음
- `app/domains/books/router.py` → 도서 관련 API 엔드포인트

### 5. **팀 협업**
- 각 팀원이 서로 다른 도메인을 담당하여 병렬 작업 가능
- Git conflict 최소화

---

## 파일 역할 설명

### 각 도메인 폴더 내부 파일:

#### `router.py`
- FastAPI 라우터 정의
- HTTP 엔드포인트 정의 (GET, POST, PATCH, DELETE)
- 요청 검증 및 응답 반환
- 예시:
```python
from fastapi import APIRouter, Depends
from app.domains.books import schemas, service
from app.core.dependencies import get_db

router = APIRouter(prefix="/api/v1/books", tags=["Books"])

@router.post("/", response_model=schemas.BookCreateResponse)
def create_book(
    request: schemas.BookCreateRequest,
    db: Session = Depends(get_db)
):
    return service.create_book(db, request)
```

#### `schemas.py`
- Pydantic 모델 정의 (요청/응답)
- 입력 검증 규칙
- API 문서화용 예시 데이터
- 예시:
```python
from pydantic import BaseModel, Field

class BookCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str
    isbn: str
    price: float
```

#### `service.py`
- 비즈니스 로직 (CRUD 작업)
- 데이터베이스 쿼리
- 외부 API 호출
- 복잡한 연산 처리
- 예시:
```python
from sqlalchemy.orm import Session
from app.models import Book

def create_book(db: Session, request: BookCreateRequest):
    book = Book(**request.dict())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book
```

---

## 공통 모듈 역할

### `app/models/`
- **역할**: SQLAlchemy ORM 모델 정의 (데이터베이스 테이블)
- **공통 사용**: 모든 도메인에서 import하여 사용
- 예: `from app.models import User, Book`

### `app/schemas/base.py`
- **역할**: 공통 응답 포맷 (BaseResponse, PaginatedResponse, ErrorResponse)
- **공통 사용**: 모든 도메인의 응답 형식 통일

### `app/core/`
- **security.py**: JWT 토큰 생성/검증, 비밀번호 해싱
- **dependencies.py**: FastAPI 의존성 함수 (`get_current_user`, `require_role`)
- **exceptions.py**: 커스텀 예외 클래스
- **error_codes.py**: 표준 에러 코드 정의

### `app/middleware/`
- **logging.py**: 모든 HTTP 요청/응답 로깅
- **error_handler.py**: 전역 예외 처리
- **cors.py**: CORS 설정

---

## main.py 구조 (라우터 등록)

```python
from fastapi import FastAPI
from app.core.middleware import setup_middleware
from app.domains.auth.router import router as auth_router
from app.domains.users.router import router as users_router
from app.domains.books.router import router as books_router
from app.domains.reviews.router import router as reviews_router
from app.domains.comments.router import router as comments_router
from app.domains.favorites.router import router as favorites_router
from app.domains.cart.router import router as cart_router
from app.domains.orders.router import router as orders_router
from app.domains.coupons.router import router as coupons_router
from app.domains.admin.router import router as admin_router
from app.domains.health.router import router as health_router

app = FastAPI(
    title="Bookstore API",
    version="1.0.0",
    description="온라인 도서 구매 시스템 API"
)

# 미들웨어 설정
setup_middleware(app)

# 라우터 등록
app.include_router(health_router)        # /health
app.include_router(auth_router)          # /api/v1/auth
app.include_router(users_router)         # /api/v1/users
app.include_router(books_router)         # /api/v1/books
app.include_router(reviews_router)       # /api/v1/reviews
app.include_router(comments_router)      # /api/v1/comments
app.include_router(favorites_router)     # /api/v1/favorites
app.include_router(cart_router)          # /api/v1/cart
app.include_router(orders_router)        # /api/v1/orders
app.include_router(coupons_router)       # /api/v1/coupons (Admin)
app.include_router(admin_router)         # /api/v1/admin (Admin)
```

---

## 도메인 간 의존성 관리

### 원칙:
1. **도메인은 models를 import** ✅
   - `from app.models import User, Book`

2. **도메인은 core를 import** ✅
   - `from app.core.dependencies import get_current_user`
   - `from app.core.exceptions import BookNotFoundException`

3. **도메인은 schemas/base를 import** ✅
   - `from app.schemas.base import BaseResponse`

4. **도메인 간 직접 import 최소화** ⚠️
   - 필요하다면 service 레벨에서만
   - 예: orders가 cart를 사용하는 경우
   - `from app.domains.cart.service import get_user_cart`

---

## 개발 워크플로우

### 1. 새로운 기능 추가 시:
1. 해당 도메인 폴더로 이동 (예: `app/domains/books/`)
2. `schemas.py`에 요청/응답 스키마 정의
3. `service.py`에 비즈니스 로직 구현
4. `router.py`에 엔드포인트 추가
5. `main.py`에 라우터 등록 (처음 한 번만)
6. 테스트 작성 (`tests/test_books.py`)

### 2. 버그 수정 시:
1. 에러 발생 도메인 확인
2. 해당 도메인의 `service.py` 또는 `router.py` 수정
3. 테스트 케이스 추가

---

## 참고: FastAPI 공식 권장 구조

FastAPI 공식 문서에서는 다음과 같은 구조를 권장합니다:
- **Small projects**: 단일 파일 또는 api/v1 폴더
- **Medium projects**: 도메인별 라우터 분리
- **Large projects**: 도메인 기반 모듈화 ← **현재 구조**

출처: https://fastapi.tiangolo.com/tutorial/bigger-applications/

---

**작성일**: 2025-12-05
**아키텍처 패턴**: Domain-Driven Design (DDD) + Layered Architecture
