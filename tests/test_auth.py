"""
Auth Domain Tests
인증 관련 엔드포인트 테스트
"""
import pytest
from datetime import date


class TestSignup:
    """회원가입 테스트"""

    def test_signup_success(self, client):
        """정상 회원가입 테스트"""
        response = client.post("/api/auth/signup", json={
            "email": "newuser@test.com",
            "password": "Password123!",
            "name": "New User",
            "birth_date": "1995-05-15",
            "gender": "MALE",
            "address": "Seoul, Korea"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["isSuccess"] is True
        assert "payload" in data
        assert "user_id" in data["payload"]
        assert "created_at" in data["payload"]

    def test_signup_duplicate_email(self, client, test_db):
        """중복 이메일 회원가입 실패 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 기존 사용자 생성
        user = User(
            email="existing@test.com",
            password=hash_password("password123!"),
            name="Existing User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()

        # 중복 이메일로 회원가입 시도
        response = client.post("/api/auth/signup", json={
            "email": "existing@test.com",
            "password": "Password123!",
            "name": "New User",
            "birth_date": "1995-05-15",
            "gender": "MALE",
            "address": "Seoul, Korea"
        })

        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "EMAIL_ALREADY_EXISTS"

    def test_signup_invalid_data(self, client):
        """잘못된 데이터로 회원가입 실패 테스트"""
        response = client.post("/api/auth/signup", json={
            "email": "invalid-email",
            "password": "short",
            "name": "",
            "birth_date": "invalid-date",
            "gender": "INVALID",
            "address": ""
        })

        assert response.status_code in [400, 422]


class TestLogin:
    """로그인 테스트"""

    def test_login_success(self, client, test_db):
        """정상 로그인 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 사용자 생성
        user = User(
            email="user@test.com",
            password=hash_password("password123!"),
            name="Test User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()

        # 로그인
        response = client.post("/api/auth/login", json={
            "email": "user@test.com",
            "password": "password123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert "access_token" in payload
        assert "refresh_token" in payload
        assert payload["token_type"] == "Bearer"
        assert "expires_in" in payload

    def test_login_invalid_credentials(self, client, test_db):
        """잘못된 자격 증명으로 로그인 실패 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 사용자 생성
        user = User(
            email="user@test.com",
            password=hash_password("password123!"),
            name="Test User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()

        # 잘못된 비밀번호로 로그인
        response = client.post("/api/auth/login", json={
            "email": "user@test.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자 로그인 실패 테스트"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123!"
        })

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"


class TestRefreshToken:
    """토큰 갱신 테스트"""

    def test_refresh_token_success(self, client, test_db):
        """정상 토큰 갱신 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 사용자 생성
        user = User(
            email="refresh_user@test.com",
            password=hash_password("password123!"),
            name="Refresh User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()

        # 로그인해서 refresh token 얻기
        response = client.post("/api/auth/login", json={
            "email": "refresh_user@test.com",
            "password": "password123!"
        })

        refresh_token = response.json()["payload"]["refresh_token"]

        # 토큰 갱신
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert "access_token" in payload
        assert payload["token_type"] == "Bearer"

    def test_refresh_token_invalid(self, client):
        """잘못된 refresh token으로 갱신 실패 테스트"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid-token"
        })

        assert response.status_code == 401


class TestLogout:
    """로그아웃 테스트"""

    def test_logout_success(self, client, test_db):
        """정상 로그아웃 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 사용자 생성
        user = User(
            email="logout_user@test.com",
            password=hash_password("password123!"),
            name="Logout User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()

        # 로그인해서 refresh token 얻기
        response = client.post("/api/auth/login", json={
            "email": "logout_user@test.com",
            "password": "password123!"
        })

        refresh_token = response.json()["payload"]["refresh_token"]

        # 로그아웃
        response = client.post("/api/auth/logout", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True

        # 로그아웃 후 같은 refresh token으로 갱신 시도 (실패해야 함)
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 401
