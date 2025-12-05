# 도서 구매 시스템 API 구현 계획서

## 프로젝트 개요
- **프로젝트명**: Bookstore API Server
- **기술 스택**: FastAPI, MySQL, JWT, Alembic
- **목표**: 온라인 도서 구매 시스템의 RESTful API 구현 및 JCloud 배포
- **총 엔드포인트**: 34개 (요구사항: 30개 이상)

---

## 1. 프로젝트 구조 설계

```
WSD_assignment_2/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 애플리케이션 진입점
│   ├── config.py                  # 환경 설정 (DB, JWT 등)
│   ├── database.py                # DB 연결 및 세션 관리
│   │
│   ├── models/                    # SQLAlchemy ORM 모델
│   │   ├── __init__.py
│   │   ├── user.py               # users, refresh_tokens
│   │   ├── book.py               # books, books_view
│   │   ├── review.py             # reviews, review_likes, review_like_counts
│   │   ├── comment.py            # comments, comment_likes
│   │   ├── favorite.py           # favorites
│   │   ├── cart.py               # carts
│   │   ├── order.py              # orders, order_items
│   │   └── coupon.py             # coupons, user_coupons
│   │
│   ├── schemas/                   # Pydantic 스키마 (요청/응답)
│   │   ├── __init__.py
│   │   ├── base.py               # 공통 응답 스키마
│   │   ├── auth.py               # 인증 관련 스키마
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── review.py
│   │   ├── comment.py
│   │   ├── favorite.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   └── coupon.py
│   │
│   ├── api/                       # API 라우터
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # 인증 (signup, login, logout, refresh)
│   │   │   ├── users.py          # 프로필 관리
│   │   │   ├── books.py          # 도서 CRUD
│   │   │   ├── reviews.py        # 리뷰 CRUD + 좋아요
│   │   │   ├── comments.py       # 댓글 CRUD + 좋아요
│   │   │   ├── favorites.py      # 위시리스트
│   │   │   ├── library.py        # 구매한 도서
│   │   │   ├── cart.py           # 장바구니
│   │   │   ├── orders.py         # 주문 관리
│   │   │   ├── coupons.py        # 쿠폰 (관리자)
│   │   │   ├── admin.py          # 관리자 전용 엔드포인트
│   │   │   └── health.py         # 헬스체크
│   │
│   ├── services/                  # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── book_service.py
│   │   ├── review_service.py
│   │   ├── order_service.py
│   │   └── cache_service.py      # 리뷰 좋아요 캐싱
│   │
│   ├── core/                      # 핵심 유틸리티
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, 비밀번호 해싱
│   │   ├── dependencies.py       # FastAPI 의존성 (인증, 권한)
│   │   ├── exceptions.py         # 커스텀 예외
│   │   └── error_codes.py        # 표준 에러 코드
│   │
│   └── middleware/                # 미들웨어
│       ├── __init__.py
│       ├── logging.py            # 요청/응답 로깅
│       ├── error_handler.py      # 전역 에러 핸들러
│       └── cors.py               # CORS 설정
│
├── alembic/                       # DB 마이그레이션
│   ├── versions/
│   └── env.py
│
├── scripts/                       # 스크립트
│   ├── seed_data.py              # 초기 데이터 (200+건)
│   └── init_db.py                # DB 초기화
│
├── tests/                         # 테스트 (20+개)
│   ├── __init__.py
│   ├── conftest.py               # 테스트 설정
│   ├── test_auth.py
│   ├── test_books.py
│   ├── test_reviews.py
│   ├── test_orders.py
│   └── test_admin.py
│
├── docs/                          # 문서
│   ├── api-design.md             # API 설계 (과제1 반영)
│   ├── db-schema.md              # DB 스키마
│   └── deployment.md             # JCloud 배포 가이드
│
├── postman/                       # Postman 컬렉션
│   └── bookstore_api.postman_collection.json
│
├── .env.example                   # 환경 변수 템플릿
├── .gitignore
├── requirements.txt
├── alembic.ini
├── README.md
└── IMPLEMENTATION_PLAN.md         # 이 문서
```

---

## 2. 데이터베이스 설계 요약

### 테이블 목록 (15개)
1. **users** - 사용자 정보 (CUSTOMER, SELLER, ADMIN)
2. **refresh_tokens** - JWT Refresh Token 관리
3. **books** - 도서 정보
4. **books_view** - 도서 조회 기록 (조회수 집계용)
5. **reviews** - 리뷰 (구매 검증 필요)
6. **review_likes** - 리뷰 좋아요
7. **review_like_counts** - 리뷰 좋아요 수 캐시 (N-Top 성능 최적화)
8. **comments** - 리뷰 댓글 (대댓글 지원)
9. **comment_likes** - 댓글 좋아요
10. **favorites** - 위시리스트 (삭제 추적)
11. **carts** - 장바구니 (삭제 추적)
12. **orders** - 주문 정보
13. **order_items** - 주문 상세 항목
14. **coupons** - 쿠폰 정보
15. **user_coupons** - 사용자 쿠폰 발급/사용 현황

### 주요 제약사항
- Foreign Key 관계 명확히 정의
- CHECK 제약조건 (role, gender, rating 등)
- UNIQUE 제약조건 (email, isbn, 중복 좋아요 방지)
- 인덱스: 검색/정렬 필드 (title, author, created_at, book_id 등)

---

## 3. API 엔드포인트 설계 (34개)

### 3.1 인증 (Auth) - 4개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/auth/signup` | auth.signup | 회원가입 |
| POST | `/api/v1/auth/login` | auth.login | 로그인 (JWT 발급) |
| POST | `/api/v1/auth/logout` | auth.logout | 로그아웃 (토큰 무효화) |
| POST | `/api/v1/auth/refresh` | auth.refresh | Access Token 재발급 |

### 3.2 사용자 프로필 (Users) - 3개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| GET | `/api/v1/users/me` | users.list | 내 프로필 조회 |
| PATCH | `/api/v1/users/me` | users.update | 프로필 수정 |
| DELETE | `/api/v1/users/me` | users.delete | 계정 삭제 |

### 3.3 도서 (Books) - 5개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/books` | books.create | 도서 등록 (SELLER) |
| GET | `/api/v1/books` | books.list | 도서 목록 (페이지네이션/검색/정렬) |
| GET | `/api/v1/books/{bookId}` | books.detail | 도서 상세 조회 |
| PATCH | `/api/v1/books/{bookId}` | books.update | 도서 수정 (SELLER) |
| DELETE | `/api/v1/books/{bookId}` | books.delete | 도서 삭제 (SELLER) |

### 3.4 리뷰 (Reviews) - 5개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/reviews` | reviews.create | 리뷰 작성 (구매 검증) |
| GET | `/api/v1/reviews` | reviews.list | 리뷰 목록 (Top-N 좋아요 순) |
| PATCH | `/api/v1/reviews/{reviewId}` | reviews.update | 리뷰 수정 (본인) |
| DELETE | `/api/v1/reviews/{reviewId}` | reviews.delete | 리뷰 삭제 (본인) |
| POST | `/api/v1/reviews/{reviewId}/like` | reviews.like | 리뷰 좋아요 토글 |

### 3.5 댓글 (Comments) - 5개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/comments` | comments.create | 댓글 작성 |
| GET | `/api/v1/comments` | comments.list | 댓글 목록 조회 |
| PATCH | `/api/v1/comments/{commentId}` | comments.update | 댓글 수정 (본인) |
| DELETE | `/api/v1/comments/{commentId}` | comments.delete | 댓글 삭제 (본인) |
| POST | `/api/v1/comments/{commentId}/like` | comments.like | 댓글 좋아요 토글 |

### 3.6 위시리스트 (Favorites) - 3개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/favorites` | favorites.add | 위시리스트 추가 |
| GET | `/api/v1/favorites` | favorites.list | 위시리스트 조회 |
| DELETE | `/api/v1/favorites/{favoriteId}` | favorites.delete | 위시리스트 삭제 |

### 3.7 라이브러리 (Library) - 1개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| GET | `/api/v1/library` | library.list | 구매한 도서 목록 (DELIVERED) |

### 3.8 장바구니 (Cart) - 4개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/cart` | cart.add | 장바구니 추가 |
| GET | `/api/v1/cart` | cart.list | 장바구니 조회 |
| PATCH | `/api/v1/cart/{cartItemId}` | cart.update | 수량 수정 |
| DELETE | `/api/v1/cart/{cartItemId}` | cart.delete | 항목 삭제 |

### 3.9 주문 (Orders) - 4개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| POST | `/api/v1/orders` | orders.create | 주문 생성 (쿠폰 적용) |
| GET | `/api/v1/orders` | orders.list | 주문 목록 (필터링) |
| GET | `/api/v1/orders/{orderId}` | orders.detail | 주문 상세 조회 |
| PATCH | `/api/v1/orders/{orderId}/cancel` | orders.cancel | 주문 취소 |

### 3.10 관리자 (Admin) - 최소 3개 (추가 구현 필요)
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| GET | `/api/v1/admin/users` | admin.listUsers | 전체 사용자 목록 (ADMIN) |
| PATCH | `/api/v1/admin/users/{userId}/role` | admin.updateRole | 사용자 역할 변경 (ADMIN) |
| GET | `/api/v1/admin/stats` | admin.getStats | 통계 조회 (판매량, 조회수 등) |
| POST | `/api/v1/admin/coupons` | admin.createCoupon | 쿠폰 생성 (ADMIN) |
| PATCH | `/api/v1/admin/orders/{orderId}/status` | admin.updateOrderStatus | 주문 상태 변경 (ADMIN) |

### 3.11 헬스체크 - 1개
| Method | Endpoint | Operation | 설명 |
|--------|----------|-----------|------|
| GET | `/health` | health.check | 서버 상태 확인 |

**총 엔드포인트: 38개** (요구사항 30개 초과 ✓)

---

## 4. 인증/인가 구현 전략

### 4.1 JWT 토큰 구조
- **Access Token**: 1시간 유효, API 요청 시 사용
- **Refresh Token**: 7일 유효, DB에 저장하여 관리
- **알고리즘**: HS256
- **Payload**: `user_id`, `email`, `role`, `exp`, `iat`

### 4.2 Role 기반 접근 제어 (RBAC)
| Role | 설명 | 접근 가능 엔드포인트 |
|------|------|---------------------|
| **CUSTOMER** | 일반 사용자 | 도서 조회, 리뷰/댓글 작성, 장바구니, 주문 |
| **SELLER** | 판매자 | CUSTOMER 권한 + 도서 등록/수정/삭제 |
| **ADMIN** | 관리자 | 전체 권한 + 사용자 관리, 통계, 쿠폰 생성 |

### 4.3 보안 구현
- **비밀번호 해싱**: bcrypt (salt rounds: 12)
- **토큰 검증**: 만료/위조 검사
- **권한 검사**: Dependency Injection 활용 (`get_current_user`, `require_role`)

---

## 5. 요청 검증 & 에러 처리

### 5.1 Pydantic 스키마 검증
- 모든 요청 Body: Field 타입, 길이, 정규식 검증
- 쿼리 파라미터: 기본값, 최대값 설정
- 예시:
  ```python
  class SignupRequest(BaseModel):
      email: EmailStr
      password: str = Field(..., min_length=8, regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])")
      name: str = Field(..., min_length=1, max_length=100)
      birth_date: date
      gender: Literal["MALE", "FEMALE"]
  ```

### 5.2 표준 에러 응답 구조
```json
{
  "timestamp": "2025-12-05T12:00:00Z",
  "path": "/api/v1/books/999",
  "status": 404,
  "code": "BOOK_NOT_FOUND",
  "message": "요청한 도서를 찾을 수 없습니다.",
  "details": {"bookId": 999}
}
```

### 5.3 에러 코드 정의 (최소 10종 이상)
| HTTP | 에러 코드 | 설명 |
|------|-----------|------|
| 400 | `BAD_REQUEST` | 잘못된 요청 형식 |
| 400 | `VALIDATION_FAILED` | 필드 검증 실패 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 |
| 401 | `TOKEN_EXPIRED` | 토큰 만료 |
| 401 | `INVALID_CREDENTIALS` | 로그인 실패 |
| 403 | `FORBIDDEN` | 권한 부족 |
| 404 | `USER_NOT_FOUND` | 사용자 없음 |
| 404 | `BOOK_NOT_FOUND` | 도서 없음 |
| 404 | `ORDER_NOT_FOUND` | 주문 없음 |
| 409 | `EMAIL_ALREADY_EXISTS` | 이메일 중복 |
| 409 | `ALREADY_LIKED` | 이미 좋아요함 |
| 422 | `ORDER_NOT_PURCHASABLE` | 주문 불가 상태 |
| 422 | `REVIEW_REQUIRES_PURCHASE` | 구매 후 리뷰 가능 |
| 500 | `INTERNAL_SERVER_ERROR` | 서버 오류 |
| 500 | `DATABASE_ERROR` | DB 연결 오류 |

---

## 6. 페이지네이션/검색/정렬

### 6.1 공통 쿼리 파라미터
```python
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")
    sort: str = Field("created_at,desc", description="정렬 필드 및 순서")
```

### 6.2 도서 검색 예시
- **엔드포인트**: `GET /api/v1/books?keyword=고양이&category=소설&sort=price,asc&page=1&size=20`
- **필터링**: title, author, publisher, isbn, category, 가격 범위
- **정렬**: price, publication_date, created_at

### 6.3 응답 구조
```json
{
  "isSuccess": true,
  "message": "도서 목록 조회 성공",
  "payload": {
    "content": [...],
    "page": 1,
    "size": 20,
    "totalElements": 153,
    "totalPages": 8,
    "sort": "price,asc"
  }
}
```

---

## 7. 시드 데이터 계획 (200+건)

| 테이블 | 데이터 수 | 내용 |
|--------|-----------|------|
| users | 50 | 일반 사용자(30), 판매자(15), 관리자(5) |
| books | 100 | 다양한 카테고리의 도서 |
| reviews | 30 | 실제 구매한 도서에 대한 리뷰 |
| comments | 20 | 리뷰에 대한 댓글 |
| orders | 25 | 다양한 상태의 주문 |
| order_items | 50 | 주문 상세 항목 |
| books_view | 200 | 도서 조회 기록 (인기 도서 집계용) |
| coupons | 10 | 활성/비활성 쿠폰 |

---

## 8. 테스트 계획 (20+개)

### 8.1 단위 테스트
- 인증 서비스 테스트 (JWT 생성, 검증)
- 비밀번호 해싱 테스트
- 에러 핸들러 테스트

### 8.2 통합 테스트 (API)
1. 회원가입 → 로그인 → 프로필 조회
2. 도서 등록 (SELLER) → 조회 → 수정 → 삭제
3. 도서 검색/정렬/페이지네이션
4. 리뷰 작성 (구매 검증 실패/성공)
5. 리뷰 좋아요 토글
6. 댓글 작성 → 좋아요
7. 위시리스트 추가 → 조회 → 삭제
8. 장바구니 추가 → 수량 수정 → 삭제
9. 주문 생성 → 상세 조회 → 취소
10. 쿠폰 적용 주문
11. 관리자 권한 테스트 (일반 사용자 접근 차단)
12. 토큰 만료 테스트
13. 중복 이메일 회원가입 실패
14. 잘못된 자격증명 로그인 실패
15. 권한 없는 리소스 접근 (403)
16. 존재하지 않는 리소스 조회 (404)
17. 필드 검증 실패 (400)
18. Refresh Token으로 Access Token 재발급
19. 로그아웃 후 토큰 무효화 확인
20. 헬스체크 엔드포인트

---

## 9. 구현 우선순위

### Phase 1: 기반 구축 (1-2일)
1. ✓ 프로젝트 구조 생성
2. ✓ 환경 설정 (.env, config.py)
3. ✓ DB 연결 및 모델 정의
4. ✓ Alembic 마이그레이션 설정
5. ✓ 공통 스키마 (BaseResponse, Pagination)

### Phase 2: 인증/인가 (1일)
6. ✓ JWT 토큰 생성/검증 (core/security.py)
7. ✓ 의존성 주입 (get_current_user, require_role)
8. ✓ Auth API (signup, login, logout, refresh)
9. ✓ 에러 핸들링 미들웨어

### Phase 3: 핵심 기능 (2-3일)
10. ✓ Users API (프로필 조회/수정/삭제)
11. ✓ Books API (CRUD + 검색/정렬/페이지네이션)
12. ✓ Reviews API (CRUD + 좋아요)
13. ✓ Comments API (CRUD + 좋아요)
14. ✓ 리뷰 좋아요 캐싱 (review_like_counts)

### Phase 4: 상거래 기능 (2일)
15. ✓ Favorites API (위시리스트)
16. ✓ Cart API (장바구니)
17. ✓ Orders API (주문 생성/조회/취소)
18. ✓ Coupon 시스템
19. ✓ Library API (구매 도서 조회)

### Phase 5: 관리자 & 고급 기능 (1일)
20. ✓ Admin API (사용자 관리, 통계)
21. ✓ 로깅 미들웨어
22. ✓ CORS 설정
23. ✓ Health Check

### Phase 6: 문서화 & 테스트 (1-2일)
24. ✓ Swagger 문서 커스터마이징
25. ✓ 시드 데이터 스크립트
26. ✓ 자동화 테스트 (pytest)
27. ✓ Postman 컬렉션 + 테스트 스크립트

### Phase 7: 배포 & 최종 점검 (1일)
28. ✓ README.md 작성
29. ✓ .env.example 생성
30. ✓ JCloud 배포
31. ✓ 최종 테스트 (모든 엔드포인트)

---

## 10. 기술적 고려사항

### 10.1 성능 최적화
- **인덱스**: books(title, author), reviews(book_id, created_at), orders(user_id, status)
- **캐싱**: review_like_counts 테이블로 Top-N 쿼리 최적화
- **N+1 방지**: SQLAlchemy의 `joinedload`, `selectinload` 활용

### 10.2 보안
- 환경 변수로 민감 정보 관리 (.env)
- bcrypt로 비밀번호 해싱
- CORS 설정 (허용 도메인 제한)
- SQL Injection 방지 (ORM 사용)
- XSS 방지 (입력 검증)

### 10.3 로깅
- 요청/응답 로그 (method, path, status, latency)
- 에러 스택트레이스 (민감정보 제외)
- 파일 로깅 (로그 로테이션)

---

## 11. 배포 체크리스트

### JCloud 배포 전
- [ ] .env 파일 서버에 업로드 (절대 Git에 커밋 금지)
- [ ] 데이터베이스 마이그레이션 실행
- [ ] 시드 데이터 생성
- [ ] 환경 변수 확인 (DB_HOST, JWT_SECRET 등)

### JCloud 배포
- [ ] 인스턴스 생성 및 포트 설정
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] uvicorn 실행 (`uvicorn app.main:app --host 0.0.0.0 --port 8080`)
- [ ] 프로세스 매니저 설정 (PM2, systemd)
- [ ] 헬스체크 확인 (`GET /health`)

### 배포 후 검증
- [ ] Swagger 문서 접근 확인 (`http://<IP>:<PORT>/docs`)
- [ ] 모든 엔드포인트 테스트 (Postman)
- [ ] 서버 재시작 후 자동 실행 확인
- [ ] 로그 파일 확인

---

## 12. 제출물 체크리스트

### GitHub Repository
- [ ] 모든 소스코드
- [ ] README.md (실행 방법, 환경 변수, 배포 주소)
- [ ] .env.example
- [ ] .gitignore (민감 정보 제외 확인)
- [ ] docs/ (api-design.md, db-schema.md)
- [ ] postman/ (컬렉션 JSON)
- [ ] tests/ (20+개 테스트)

### Classroom 제출
- [ ] GitHub Public Repo 주소
- [ ] DB 접속 정보 (텍스트/워드 파일)
- [ ] JCloud 접속 키 파일 (.pem)
- [ ] .env 파일
- [ ] Swagger 주소 + 포트
- [ ] API Root 주소

---

## 13. 참고 자료

- FastAPI 공식 문서: https://fastapi.tiangolo.com/
- SQLAlchemy 문서: https://docs.sqlalchemy.org/
- Alembic 마이그레이션: https://alembic.sqlalchemy.org/
- JWT 토큰: https://jwt.io/
- bcrypt 해싱: https://pypi.org/project/bcrypt/
- pytest 테스트: https://docs.pytest.org/

---

**작성일**: 2025-12-05
**예상 완료일**: 2025-12-13 (제출 마감: 12월 14일 23:59)
