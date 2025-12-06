"""
Pytest Configuration and Fixtures
테스트용 데이터베이스 및 클라이언트 설정
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base
from app.core.dependencies import get_db

# 테스트용 데이터베이스 경로
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """각 테스트마다 새로운 데이터베이스 생성"""
    # 테스트 엔진 생성
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 세션 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI 테스트 클라이언트"""
    from app.main import app

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client, test_db):
    """관리자 토큰 생성"""
    from app.models import User, UserRole, Gender
    from app.core.security import hash_password
    from datetime import date

    # 관리자 생성
    admin = User(
        email="admin@test.com",
        password=hash_password("admin123!"),
        name="Admin User",
        birth_date=date(1990, 1, 1),
        gender=Gender.MALE,
        address="Test Address",
        role=UserRole.ADMIN
    )
    test_db.add(admin)
    test_db.commit()

    # 로그인
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123!"
    })

    return response.json()["payload"]["access_token"]


@pytest.fixture(scope="function")
def seller_token(client, test_db):
    """판매자 토큰 생성"""
    from app.models import User, UserRole, Gender
    from app.core.security import hash_password
    from datetime import date

    # 판매자 생성
    seller = User(
        email="seller@test.com",
        password=hash_password("seller123!"),
        name="Seller User",
        birth_date=date(1990, 1, 1),
        gender=Gender.MALE,
        address="Test Address",
        role=UserRole.SELLER
    )
    test_db.add(seller)
    test_db.commit()

    # 로그인
    response = client.post("/api/auth/login", json={
        "email": "seller@test.com",
        "password": "seller123!"
    })

    return response.json()["payload"]["access_token"]


@pytest.fixture(scope="function")
def customer_token(client, test_db):
    """고객 토큰 생성"""
    from app.models import User, UserRole, Gender
    from app.core.security import hash_password
    from datetime import date

    # 고객 생성
    customer = User(
        email="customer@test.com",
        password=hash_password("customer123!"),
        name="Customer User",
        birth_date=date(1990, 1, 1),
        gender=Gender.MALE,
        address="Test Address",
        role=UserRole.CUSTOMER
    )
    test_db.add(customer)
    test_db.commit()

    # 로그인
    response = client.post("/api/auth/login", json={
        "email": "customer@test.com",
        "password": "customer123!"
    })

    return response.json()["payload"]["access_token"]
