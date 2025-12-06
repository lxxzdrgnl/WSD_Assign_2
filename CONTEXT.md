# 프로젝트 컨텍스트 (Claude 초기화 대비)

## 🎯 프로젝트 정보
- **프로젝트명**: Bookstore API (FastAPI 기반 도서 구매 시스템)
- **현재 DB**: SQLite (개발용) → MySQL (배포용)
- **진행률**: 5/38 엔드포인트 (13%)
- **마감**: 2025-12-14 23:59

## ✅ 완료된 작업
1. 프로젝트 구조: 도메인 기반 (`app/domains/`)
2. DB 모델: 15개 테이블 (app/models/)
3. **중요**: PRIMARY KEY 모두 `INTEGER`로 변경 (SQLite autoincrement)
4. 인증: JWT + bcrypt (72-byte 처리), RBAC
5. 완료 엔드포인트: /health, /api/v1/auth/* (signup, login, logout, refresh)

## 📊 데이터베이스 스키마 (15개 테이블)

### users | 이용자 정보
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT  -- SQLite는 INTEGER만 autoincrement 지원!
role VARCHAR(8) NOT NULL              -- CUSTOMER, SELLER, ADMIN
email VARCHAR(255) UNIQUE NOT NULL
password VARCHAR(255) NOT NULL        -- bcrypt 해시
name VARCHAR(255) NOT NULL
birth_date DATE NOT NULL
gender VARCHAR(6) NOT NULL            -- MALE, FEMALE
address VARCHAR(255)
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### refresh_tokens | 인증 토큰
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE CASCADE
token VARCHAR(500) UNIQUE NOT NULL
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### books | 도서 정보
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
seller_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
title VARCHAR(255) NOT NULL INDEX
author VARCHAR(100) NOT NULL INDEX
publisher VARCHAR(100) NOT NULL
summary VARCHAR(500)
isbn VARCHAR(20) UNIQUE NOT NULL INDEX
price DECIMAL(15,2) NOT NULL
publication_date DATE NOT NULL
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### books_view | 도서 조회 기록 (조회수/인기도서)
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE SET NULL
book_id BIGINT FK(books.id) ON DELETE CASCADE
viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### reviews | 리뷰
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
book_id BIGINT FK(books.id) ON DELETE CASCADE INDEX
order_id BIGINT FK(orders.id) ON DELETE RESTRICT INDEX  -- 구매 검증 필요!
comment TEXT NOT NULL
rating INTEGER CHECK(rating >= 1 AND rating <= 5) NOT NULL
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### review_likes | 리뷰 좋아요
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
review_id BIGINT FK(reviews.id) ON DELETE CASCADE INDEX
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
UNIQUE(review_id, user_id)  -- 중복 좋아요 방지
```

### review_like_counts | 리뷰 좋아요 수 캐시 (N-Top 성능)
```sql
review_id BIGINT PRIMARY KEY FK(reviews.id) ON DELETE CASCADE
like_count INTEGER DEFAULT 0 NOT NULL
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### comments | 리뷰 댓글
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
review_id BIGINT FK(reviews.id) ON DELETE CASCADE INDEX
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
parent_comment_id BIGINT FK(comments.id) ON DELETE CASCADE  -- NULL이면 일반, 값 있으면 대댓글
content TEXT NOT NULL
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### comment_likes | 댓글 좋아요
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
comment_id BIGINT FK(comments.id) ON DELETE CASCADE INDEX
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
UNIQUE(comment_id, user_id)  -- 중복 좋아요 방지
```

### favorites | 위시리스트 (삭제 추적)
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
book_id BIGINT FK(books.id) ON DELETE CASCADE INDEX
is_deleted BOOLEAN DEFAULT FALSE NOT NULL  -- 통계용
deleted_at DATETIME
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### carts | 장바구니 (삭제 추적)
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
book_id BIGINT FK(books.id) ON DELETE CASCADE INDEX
quantity INTEGER DEFAULT 1 NOT NULL
is_deleted BOOLEAN DEFAULT FALSE NOT NULL  -- 통계용
deleted_at DATETIME
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### orders | 주문
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE SET NULL INDEX
total_price DECIMAL(15,2) NOT NULL
status VARCHAR(9) NOT NULL INDEX  -- CREATED, PAID, SHIPPED, DELIVERED, CANCELED
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### order_items | 주문 상세
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
order_id BIGINT FK(orders.id) ON DELETE CASCADE INDEX
book_id BIGINT FK(books.id) ON DELETE SET NULL
quantity INTEGER NOT NULL
price_at_purchase DECIMAL(15,2) NOT NULL  -- 구매 당시 가격
```

### coupons | 쿠폰
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
name VARCHAR(100) NOT NULL
description VARCHAR(255)
discount_rate DECIMAL(5,2) NOT NULL  -- 할인율 (%)
start_at DATETIME DEFAULT CURRENT_TIMESTAMP
end_at DATETIME NOT NULL
is_active BOOLEAN DEFAULT TRUE NOT NULL
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

### user_coupons | 사용자 쿠폰 발급/사용
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
user_id BIGINT FK(users.id) ON DELETE CASCADE INDEX
coupon_id BIGINT FK(coupons.id) ON DELETE CASCADE INDEX
is_used BOOLEAN DEFAULT FALSE NOT NULL
used_at DATETIME
assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

## 📁 프로젝트 구조
```
app/
├── domains/          # 도메인별 router, schemas, service
│   └── auth/         # ✅ 완료
├── models/           # SQLAlchemy 모델 (15개 테이블) ✅
├── core/             # security.py, dependencies.py, exceptions.py ✅
├── middleware/       # error_handler.py ✅
├── config.py         # ✅
├── database.py       # ✅
└── main.py           # ✅
```

## 🔑 핵심 구현 (초기화 후 필수 확인)

### 1. bcrypt 비밀번호 (app/core/security.py)
```python
import bcrypt  # passlib 아님!

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]  # 72-byte 제한
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
```

### 2. JWT 토큰 (app/core/security.py)
- Access Token: 1시간 (ACCESS_TOKEN_EXPIRE_MINUTES=60)
- Refresh Token: 7일 (REFRESH_TOKEN_EXPIRE_DAYS=7)
- Payload: {user_id, email, role, exp, iat, type}

### 3. 응답 구조 (app/schemas/base.py)
```json
{
  "isSuccess": true,
  "message": "Success",
  "payload": {...}
}
```

### 4. 에러 응답 (app/middleware/error_handler.py)
```json
{
  "timestamp": "2025-12-06T...",
  "path": "/api/v1/...",
  "status": 404,
  "code": "BOOK_NOT_FOUND",
  "message": "...",
  "details": {...}
}
```

## 🚀 다음 작업 (우선순위)

### 1. Books 도메인 (5개) - 다음 작업!
```
POST   /api/v1/books               # 도서 등록 (SELLER)
GET    /api/v1/books               # 목록 + 검색/정렬/페이지네이션
GET    /api/v1/books/{bookId}      # 상세 조회
PATCH  /api/v1/books/{bookId}      # 수정 (SELLER)
DELETE /api/v1/books/{bookId}      # 삭제 (SELLER)
```
**검색**: keyword, author, publisher, min_price, max_price
**정렬**: price, publication_date, created_at (asc/desc)
**페이지**: page=1, size=10

### 2. Users 도메인 (3개)
```
GET    /api/v1/users/me
PATCH  /api/v1/users/me
DELETE /api/v1/users/me
```

### 3. Reviews 도메인 (5개) - 구매 검증 필수
### 4. Comments 도메인 (5개) - 대댓글 지원
### 5. 나머지: Favorites, Cart, Orders, Library, Admin

## 🔧 환경 설정

### .env
```bash
DATABASE_URL=sqlite:///./bookstore.db
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 서버 실행
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 테스트
```bash
# Health
curl http://localhost:8080/health

# Signup
curl -X POST http://localhost:8080/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","name":"테스트","birth_date":"1990-01-01","gender":"MALE"}'

# Login
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

## ⚠️ 주의사항 (초기화 후 필수 확인)

1. **SQLite PRIMARY KEY** - 반드시 `INTEGER` (BIGINT 안됨!)
2. **bcrypt 직접 사용** - passlib 아님
3. **도메인 구조** - `app/domains/{domain}/router.py, schemas.py, service.py`
4. **비밀번호 검증** - Pydantic에서 대소문자+숫자+특수문자 필수
5. **모든 모델 Integer import** - `from sqlalchemy import Column, Integer, BigInteger, ...`

## 📝 참고 파일
- **CONTEXT.md** (이 파일) - 초기화 후 필수 정보
- **claude.md** - 전체 API 설계 및 구현 계획
- **app/models/*.py** - 15개 테이블 전체 정의
- **app/domains/auth/** - Auth 엔드포인트 구현 예시

---
**최종 업데이트**: 2025-12-06
**진행률**: 5/38 (13%)
