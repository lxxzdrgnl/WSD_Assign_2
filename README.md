# Bookstore API

온라인 도서 구매 시스템 RESTful API

---

## 프로젝트 개요

### 문제 정의
사용자가 온라인으로 도서를 검색, 구매, 리뷰 작성 및 관리할 수 있는 전자상거래 플랫폼이 필요합니다. 판매자는 도서를 등록하고 관리할 수 있으며, 관리자는 사용자 및 주문을 관리할 수 있는 시스템이 요구됩니다.

### 주요 기능 목록
- **인증 및 권한 관리**: JWT 기반 회원가입, 로그인, 토큰 갱신, 로그아웃
- **사용자 관리**: 프로필 조회/수정, 회원 탈퇴
- **도서 관리**: 도서 등록(판매자), 조회, 수정, 삭제, 검색 및 필터링
- **리뷰 시스템**: 구매 도서 리뷰 작성, 수정, 삭제, 좋아요
- **댓글 시스템**: 리뷰에 댓글 작성, 수정, 삭제, 좋아요
- **찜 기능**: 도서 찜하기, 찜 목록 조회, 찜 해제
- **장바구니**: 장바구니 추가, 조회, 수량 수정, 삭제
- **주문 관리**: 주문 생성, 조회, 취소, 쿠폰 적용
- **내 서재**: 구매한 도서 목록 조회
- **쿠폰 시스템**: 쿠폰 조회, 관리자 쿠폰 생성 및 발급
- **관리자 기능**: 사용자 역할 변경, 주문 상태 변경, 통계 조회

---

## 실행 방법

### 로컬 실행

#### 1. 의존성 설치
```bash
# Python 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

#### 2. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 설정합니다.
```bash
cp .env.example .env
```

#### 3. 데이터베이스 마이그레이션 및 시드
```bash
# Docker로 MySQL 실행 (권장)
docker-compose up -d db

# Alembic 마이그레이션 실행
alembic upgrade head

# 시드 데이터 생성 (선택사항)
python scripts/seed_data.py
```

#### 4. 서버 실행
```bash
# 개발 서버 실행 (Hot Reload)
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 또는 Docker Compose로 전체 실행
docker-compose up -d
```

#### 5. 접속 확인
- **Base URL**: http://localhost:8080
- **Swagger Docs**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

---

## 환경 변수 설명

`.env.example` 파일을 참고하여 다음 환경 변수를 설정하세요:

| 변수명 | 설명 | 기본값 | 비고 |
|--------|------|--------|------|
| `APP_NAME` | 애플리케이션 이름 | Bookstore API | - |
| `APP_VERSION` | 애플리케이션 버전 | 1.0.0 | - |
| `DEBUG` | 디버그 모드 | True | 프로덕션에서는 False |
| `ENVIRONMENT` | 실행 환경 | development | production, staging 등 |
| `HOST` | 서버 호스트 | 0.0.0.0 | - |
| `PORT` | 서버 포트 | 8080 | - |
| `DB_HOST` | DB 호스트 | db | Docker 사용 시 서비스명, 로컬은 localhost |
| `DB_PORT` | DB 포트 | 3306 | - |
| `DB_USER` | DB 사용자명 | your_db_user | **필수 변경** |
| `DB_PASSWORD` | DB 비밀번호 | your_db_password | **필수 변경** |
| `DB_NAME` | DB 이름 | bookstore_db | - |
| `DB_ROOT_PASSWORD` | DB Root 비밀번호 | your_strong_root_password | **필수 변경** (Docker 사용 시) |
| `JWT_SECRET_KEY` | JWT 서명 키 | your-secret-key-here | **필수 변경** (강력한 랜덤 문자열) |
| `JWT_ALGORITHM` | JWT 알고리즘 | HS256 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 시간 (분) | 60 | - |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 시간 (일) | 7 | - |
| `BCRYPT_ROUNDS` | Bcrypt 해싱 라운드 | 12 | - |

---

## 배포 주소

### 프로덕션 환경
- **Base URL**: http://113.198.66.68:10040
- **API Root**: http://113.198.66.68:10040/api
- **Swagger URL**: http://113.198.66.68:10040/docs
- **ReDoc URL**: http://113.198.66.68:10040/redoc
- **Health Check URL**: http://113.198.66.68:10040/health

### SSH 접속
```bash
ssh -i jcloud.pem -p 19040 ubuntu@113.198.66.68
```

---

## 인증 플로우 설명

### 1. 회원가입
```
POST /api/auth/signup
- 이메일, 비밀번호, 이름, 생년월일, 성별, 주소 입력
- 비밀번호는 bcrypt로 해싱되어 저장
- 기본 역할: CUSTOMER
```

### 2. 로그인
```
POST /api/auth/login
- 이메일, 비밀번호로 인증
- 성공 시 Access Token (1시간) 및 Refresh Token (7일) 발급
- Refresh Token은 DB에 저장됨
```

### 3. 토큰 사용
```
- 모든 인증 필요 API는 Authorization 헤더에 Bearer Token 필요
- Header: Authorization: Bearer {access_token}
```

### 4. 토큰 갱신
```
POST /api/auth/refresh
- Refresh Token으로 새로운 Access Token 발급
- Refresh Token은 재사용 가능 (만료 전까지)
```

### 5. 로그아웃
```
POST /api/auth/logout
- Refresh Token을 DB에서 삭제하여 무효화
```

---

## 역할/권한표

| 역할 | 설명 | 주요 권한 |
|------|------|-----------|
| **CUSTOMER** | 일반 사용자 | 도서 조회, 구매, 리뷰 작성, 장바구니, 찜, 프로필 관리 |
| **SELLER** | 판매자 | CUSTOMER 권한 + 도서 등록/수정/삭제 |
| **ADMIN** | 관리자 | 모든 권한 + 사용자 관리, 주문 관리, 통계 조회, 쿠폰 생성/발급 |

### API별 접근 권한

| 기능 | 엔드포인트 | CUSTOMER | SELLER | ADMIN |
|------|-----------|----------|--------|-------|
| **인증** |
| 회원가입 | POST /api/auth/signup | ✅ | ✅ | ✅ |
| 로그인 | POST /api/auth/login | ✅ | ✅ | ✅ |
| 토큰 갱신 | POST /api/auth/refresh | ✅ | ✅ | ✅ |
| 로그아웃 | POST /api/auth/logout | ✅ | ✅ | ✅ |
| **사용자** |
| 내 프로필 조회 | GET /api/users/me | ✅ | ✅ | ✅ |
| 프로필 수정 | PATCH /api/users/me | ✅ | ✅ | ✅ |
| 회원 탈퇴 | DELETE /api/users/me | ✅ | ✅ | ✅ |
| **도서** |
| 도서 목록 조회 | GET /api/books | ✅ (공개) | ✅ (공개) | ✅ (공개) |
| 도서 상세 조회 | GET /api/books/{id} | ✅ (공개) | ✅ (공개) | ✅ (공개) |
| 도서 등록 | POST /api/books | ❌ | ✅ | ✅ |
| 도서 수정 | PATCH /api/books/{id} | ❌ | ✅ (본인) | ✅ |
| 도서 삭제 | DELETE /api/books/{id} | ❌ | ✅ (본인) | ✅ |
| **리뷰** |
| 리뷰 작성 | POST /api/reviews | ✅ (구매자) | ✅ (구매자) | ✅ |
| 리뷰 조회 | GET /api/reviews | ✅ (공개) | ✅ (공개) | ✅ (공개) |
| 리뷰 수정 | PATCH /api/reviews/{id} | ✅ (본인) | ✅ (본인) | ✅ |
| 리뷰 삭제 | DELETE /api/reviews/{id} | ✅ (본인) | ✅ (본인) | ✅ |
| 리뷰 좋아요 | POST /api/reviews/{id}/like | ✅ | ✅ | ✅ |
| **댓글** |
| 댓글 작성 | POST /api/comments | ✅ | ✅ | ✅ |
| 댓글 조회 | GET /api/comments | ✅ (공개) | ✅ (공개) | ✅ (공개) |
| 댓글 수정 | PATCH /api/comments/{id} | ✅ (본인) | ✅ (본인) | ✅ |
| 댓글 삭제 | DELETE /api/comments/{id} | ✅ (본인) | ✅ (본인) | ✅ |
| 댓글 좋아요 | POST /api/comments/{id}/like | ✅ | ✅ | ✅ |
| **찜** |
| 찜 추가 | POST /api/favorites | ✅ | ✅ | ✅ |
| 찜 목록 조회 | GET /api/favorites | ✅ | ✅ | ✅ |
| 찜 해제 | DELETE /api/favorites/{book_id} | ✅ | ✅ | ✅ |
| **장바구니** |
| 장바구니 추가 | POST /api/cart | ✅ | ✅ | ✅ |
| 장바구니 조회 | GET /api/cart | ✅ | ✅ | ✅ |
| 수량 수정 | PATCH /api/cart/{cart_id} | ✅ | ✅ | ✅ |
| 장바구니 삭제 | DELETE /api/cart/{cart_id} | ✅ | ✅ | ✅ |
| **주문** |
| 주문 생성 | POST /api/orders | ✅ | ✅ | ✅ |
| 주문 목록 조회 | GET /api/orders | ✅ | ✅ | ✅ |
| 주문 상세 조회 | GET /api/orders/{id} | ✅ (본인) | ✅ (본인) | ✅ |
| 주문 취소 | PATCH /api/orders/{id}/cancel | ✅ (본인) | ✅ (본인) | ✅ |
| **내 서재** |
| 구매 도서 목록 | GET /api/library | ✅ | ✅ | ✅ |
| **쿠폰** |
| 내 쿠폰 조회 | GET /api/coupons/me | ✅ | ✅ | ✅ |
| 사용 가능 쿠폰 조회 | GET /api/coupons/available | ✅ | ✅ | ✅ |
| **관리자** |
| 전체 사용자 조회 | GET /api/admin/users | ❌ | ❌ | ✅ |
| 사용자 역할 변경 | PATCH /api/admin/users/{id}/role | ❌ | ❌ | ✅ |
| 통계 조회 | GET /api/admin/stats | ❌ | ❌ | ✅ |
| 주문 상태 변경 | PATCH /api/admin/orders/{id}/status | ❌ | ❌ | ✅ |
| 쿠폰 생성 | POST /api/admin/coupons | ❌ | ❌ | ✅ |
| 쿠폰 발급 | POST /api/admin/coupons/{id}/issue/{user_id} | ❌ | ❌ | ✅ |

---

## 예제 계정

### 관리자 (ADMIN)
```
이메일: admin@bookstore.com
비밀번호: admin123!
```
**⚠️ 주의사항**:
- 모든 사용자 및 주문 데이터 접근 가능
- 사용자 역할 변경, 주문 상태 변경 가능
- 쿠폰 생성 및 발급 권한 보유
- **프로덕션 환경에서는 반드시 비밀번호를 변경하세요**

### 판매자 (SELLER)
```
이메일: seller1@bookstore.com
비밀번호: seller1123!
```
**권한**: 도서 등록, 수정, 삭제 + 일반 사용자 권한

추가 판매자 계정: `seller2@bookstore.com` ~ `seller9@bookstore.com` (비밀번호: `seller{N}123!`)

### 일반 사용자 (CUSTOMER)
```
이메일: customer1@example.com
비밀번호: customer1123!
```
**권한**: 도서 조회, 구매, 리뷰 작성, 장바구니, 찜, 프로필 관리

추가 사용자 계정: `customer2@example.com` ~ `customer40@example.com` (비밀번호: `customer{N}123!`)

---

## DB 연결 정보 (테스트용)

### Docker Compose 환경
```
Host: localhost
Port: 3307 (외부 접속용, 컨테이너 내부는 3306)
Database: bookstore_db
User: (환경변수 DB_USER 참조)
Password: (환경변수 DB_PASSWORD 참조)
```

### 컨테이너 내부 연결
```
Host: db
Port: 3306
Database: bookstore_db
```

### 접속 예시
```bash
# MySQL CLI로 접속
mysql -h localhost -P 3307 -u your_db_user -p

# 또는 Docker 컨테이너 직접 접속
docker exec -it wsd_assignment_2-db-1 mysql -u root -p
```

**⚠️ 권한 범위**:
- 테스트용 계정은 `bookstore_db` 데이터베이스에만 접근 가능
- Root 계정은 보안상 외부 접속 비활성화 권장

---

## 엔드포인트 요약표

### 인증 (Auth)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/auth/signup` | 회원가입 | ❌ |
| POST | `/api/auth/login` | 로그인 | ❌ |
| POST | `/api/auth/refresh` | 토큰 갱신 | ❌ |
| POST | `/api/auth/logout` | 로그아웃 | ✅ |

### 사용자 (Users)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/api/users/me` | 내 프로필 조회 | ✅ |
| PATCH | `/api/users/me` | 프로필 수정 | ✅ |
| DELETE | `/api/users/me` | 회원 탈퇴 | ✅ |

### 도서 (Books)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/api/books` | 도서 목록 조회 (검색/필터/정렬) | ❌ |
| GET | `/api/books/{book_id}` | 도서 상세 조회 | ❌ |
| POST | `/api/books` | 도서 등록 (판매자) | ✅ (SELLER/ADMIN) |
| PATCH | `/api/books/{book_id}` | 도서 수정 (판매자) | ✅ (SELLER/ADMIN) |
| DELETE | `/api/books/{book_id}` | 도서 삭제 (판매자) | ✅ (SELLER/ADMIN) |

### 리뷰 (Reviews)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/reviews` | 리뷰 작성 (구매자만) | ✅ |
| GET | `/api/reviews` | 리뷰 목록 조회 | ❌ |
| GET | `/api/reviews/{review_id}` | 리뷰 상세 조회 | ❌ |
| PATCH | `/api/reviews/{review_id}` | 리뷰 수정 (본인) | ✅ |
| DELETE | `/api/reviews/{review_id}` | 리뷰 삭제 (본인) | ✅ |
| POST | `/api/reviews/{review_id}/like` | 리뷰 좋아요 토글 | ✅ |

### 댓글 (Comments)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/comments` | 댓글 작성 | ✅ |
| GET | `/api/comments` | 댓글 목록 조회 | ❌ |
| GET | `/api/comments/{comment_id}` | 댓글 상세 조회 | ❌ |
| PATCH | `/api/comments/{comment_id}` | 댓글 수정 (본인) | ✅ |
| DELETE | `/api/comments/{comment_id}` | 댓글 삭제 (본인) | ✅ |
| POST | `/api/comments/{comment_id}/like` | 댓글 좋아요 토글 | ✅ |

### 찜 (Favorites)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/favorites` | 찜 추가 | ✅ |
| GET | `/api/favorites` | 찜 목록 조회 | ✅ |
| DELETE | `/api/favorites/{book_id}` | 찜 해제 | ✅ |

### 장바구니 (Cart)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/cart` | 장바구니 추가 | ✅ |
| GET | `/api/cart` | 장바구니 조회 | ✅ |
| PATCH | `/api/cart/{cart_id}` | 수량 수정 | ✅ |
| DELETE | `/api/cart/{cart_id}` | 장바구니 삭제 | ✅ |

### 주문 (Orders)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| POST | `/api/orders` | 주문 생성 | ✅ |
| GET | `/api/orders` | 주문 목록 조회 | ✅ |
| GET | `/api/orders/{order_id}` | 주문 상세 조회 | ✅ |
| PATCH | `/api/orders/{order_id}/cancel` | 주문 취소 | ✅ |

### 내 서재 (Library)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/api/library` | 구매한 도서 목록 | ✅ |

### 쿠폰 (Coupons)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/api/coupons/me` | 내 쿠폰 목록 | ✅ |
| GET | `/api/coupons/available` | 사용 가능 쿠폰 | ✅ |

### 관리자 (Admin)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/api/admin/users` | 전체 사용자 조회 | ✅ (ADMIN) |
| PATCH | `/api/admin/users/{user_id}/role` | 사용자 역할 변경 | ✅ (ADMIN) |
| GET | `/api/admin/stats` | 통계 조회 | ✅ (ADMIN) |
| PATCH | `/api/admin/orders/{order_id}/status` | 주문 상태 변경 | ✅ (ADMIN) |
| POST | `/api/admin/coupons` | 쿠폰 생성 | ✅ (ADMIN) |
| POST | `/api/admin/coupons/{coupon_id}/issue/{user_id}` | 쿠폰 발급 | ✅ (ADMIN) |

### 헬스 체크 (Health)
| 메서드 | URL | 설명 | 인증 필요 |
|--------|-----|------|----------|
| GET | `/health` | 서버 상태 확인 | ❌ |

---

## 성능/보안 고려사항

### 보안 (Security)
1. **비밀번호 암호화**: bcrypt 사용 (12 rounds)
2. **JWT 토큰**: HS256 알고리즘, Access Token (1시간), Refresh Token (7일)
3. **Refresh Token 관리**: DB에 저장하여 로그아웃 시 무효화
4. **Rate Limiting**: SlowAPI 사용
   - 회원가입/로그인: 10회/분
   - 토큰 갱신/로그아웃: 60회/분
   - 도서 등록: 30회/분
   - 도서 조회: 100회/분
5. **CORS 설정**: 허용된 도메인만 접근 가능 (프로덕션 환경)
6. **입력 검증**: Pydantic 스키마를 통한 모든 입력 검증
7. **SQL Injection 방지**: SQLAlchemy ORM 사용
8. **권한 검증**: 의존성 함수를 통한 역할 기반 접근 제어 (RBAC)

### 성능 (Performance)
1. **DB 인덱스**:
   - `users.email`: UNIQUE INDEX
   - `users.id`: PRIMARY KEY
   - `books.seller_id`: INDEX (외래키)
   - `reviews.book_id`, `reviews.user_id`: INDEX
   - `refresh_tokens.token`: UNIQUE INDEX
   - `refresh_tokens.user_id`: INDEX
2. **페이지네이션**: 모든 목록 조회 API에 페이지네이션 적용 (기본 10개, 최대 100개)
3. **정렬 옵션**: 대부분의 목록 조회 API에서 정렬 기준 및 순서 지정 가능
4. **선택적 인증**: 공개 API에서는 선택적 인증으로 성능 개선
5. **연결 풀링**: SQLAlchemy 기본 연결 풀 사용

### 로깅 (Logging)
- **요청/응답 로깅**: 모든 HTTP 요청/응답 로그 기록
- **에러 추적**: 전역 예외 핸들러를 통한 에러 로깅

### 에러 처리
- **통일된 에러 응답**: 모든 에러는 표준 JSON 형식으로 응답
- **상세한 에러 메시지**: 개발 환경에서는 상세한 에러 정보 제공
- **HTTP 상태 코드**: RESTful 표준에 따른 적절한 상태 코드 사용

---

## 한계와 개선 계획

### 현재 한계점

1. **파일 업로드 미지원**
   - 도서 썸네일, 사용자 프로필 이미지 업로드 기능 없음
   - **개선 계획**: AWS S3 또는 Cloudinary 연동

2. **결제 시스템 미구현**
   - 실제 결제 처리 없이 주문만 생성
   - **개선 계획**: Stripe, PayPal, 토스페이먼츠 등 PG 연동

3. **재고 관리 미구현**
   - 도서 재고 추적 및 관리 기능 부재
   - **개선 계획**: `books.stock` 필드 추가 및 주문 시 재고 차감 로직

4. **알림 기능 없음**
   - 주문 상태 변경, 리뷰 답글 등에 대한 알림 미제공
   - **개선 계획**: 이메일 알림 (SendGrid, AWS SES) 또는 푸시 알림

5. **검색 성능**
   - LIKE 쿼리 기반 검색으로 대용량 데이터에서 성능 저하 가능
   - **개선 계획**: Elasticsearch 또는 MySQL Full-Text Search 도입

6. **캐싱 미적용**
   - 자주 조회되는 데이터에 대한 캐싱 없음
   - **개선 계획**: Redis 캐싱 레이어 추가 (도서 목록, 통계 등)

7. **배송 관리 미구현**
   - 배송지 관리, 배송 추적 기능 없음
   - **개선 계획**: 배송 API 연동 및 배송 상태 추적

8. **쿠폰 자동 발급 미지원**
   - 관리자가 수동으로 발급만 가능
   - **개선 계획**: 조건부 자동 발급 (신규 회원, 생일 등)

9. **로그 관리 개선 필요**
   - 파일 기반 로깅만 사용
   - **개선 계획**: ELK Stack 또는 CloudWatch Logs 연동

10. **테스트 커버리지 부족**
    - 일부 도메인만 단위 테스트 존재
    - **개선 계획**: 통합 테스트 및 E2E 테스트 추가, 90% 이상 커버리지 목표

### 추가 개선 사항

- **API 버저닝**: URL 기반 버저닝 (`/api/v1`, `/api/v2`)
- **GraphQL 지원**: 클라이언트 요구에 따른 유연한 데이터 조회
- **WebSocket**: 실시간 주문 상태 업데이트
- **CI/CD 파이프라인**: GitHub Actions, Jenkins 등을 통한 자동 배포
- **모니터링**: Prometheus + Grafana 또는 Datadog 연동
- **마이크로서비스 전환**: 도서, 주문, 결제 등 도메인별 서비스 분리

---

## 기술 스택

- **Framework**: FastAPI 0.123.9
- **Language**: Python 3.10+
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0.36
- **Migration**: Alembic 1.13.1
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic 2.12.5
- **Rate Limiting**: SlowAPI
- **Server**: Uvicorn 0.38.0
- **Containerization**: Docker, Docker Compose

---

## 라이선스

이 프로젝트는 교육 목적으로 작성되었습니다.

---

## 문의

프로젝트 관련 문의사항은 이슈 트래커를 이용해주세요.
