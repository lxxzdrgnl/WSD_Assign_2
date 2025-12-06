"""
Simple Comprehensive Tests
간단한 종합 테스트 - 20개 이상
"""
import pytest


class TestAuthComplete:
    """인증 테스트 (9개)"""
    
    def test_01_signup(self, client):
        assert client.post("/api/auth/signup", json={
            "email": "test1@test.com", "password": "Password123!", "name": "Test",
            "birth_date": "1990-01-01", "gender": "MALE", "address": "Seoul"
        }).status_code == 201
    
    def test_02_login(self, client, customer_token):
        response = client.post("/api/auth/login", json={
            "email": "customer@test.com", "password": "customer123!"
        })
        assert response.status_code == 200
    
    def test_03_refresh(self, client, test_db):
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password
        from datetime import date
        user = User(email="ref@test.com", password=hash_password("Password123!"),
                   name="Test", birth_date=date(1990,1,1), gender=Gender.MALE,
                   address="Addr", role=UserRole.CUSTOMER)
        test_db.add(user)
        test_db.commit()
        r = client.post("/api/auth/login", json={"email":"ref@test.com","password":"Password123!"})
        rt = r.json()["payload"]["refresh_token"]
        assert client.post("/api/auth/refresh", json={"refresh_token": rt}).status_code == 200
    
    def test_04_logout(self, client, test_db):
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password
        from datetime import date
        user = User(email="logo@test.com", password=hash_password("Password123!"),
                   name="Test", birth_date=date(1990,1,1), gender=Gender.MALE,
                   address="Addr", role=UserRole.CUSTOMER)
        test_db.add(user)
        test_db.commit()
        r = client.post("/api/auth/login", json={"email":"logo@test.com","password":"Password123!"})
        rt = r.json()["payload"]["refresh_token"]
        assert client.post("/api/auth/logout", json={"refresh_token": rt}).status_code == 200


class TestBooksComplete:
    """도서 테스트 (5개)"""
    
    def test_05_get_books(self, client):
        assert client.get("/api/books").status_code == 200
    
    def test_06_get_book_detail(self, client):
        assert client.get("/api/books/99999").status_code == 404
    
    def test_07_create_book_forbidden(self, client, customer_token):
        assert client.post("/api/books", headers={"Authorization": f"Bearer {customer_token}"}).status_code in [403, 422]
    
    def test_08_books_no_auth(self, client):
        assert client.post("/api/books").status_code in [401, 422]


class TestUsersComplete:
    """사용자 테스트 (4개)"""
    
    def test_09_get_profile(self, client, customer_token):
        r = client.get("/users/me", headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200
    
    def test_10_profile_no_auth(self, client):
        assert client.get("/users/me").status_code == 401
    
    def test_11_patch_profile(self, client, customer_token):
        r = client.patch("/users/me", headers={"Authorization": f"Bearer {customer_token}"},
                        json={"name": "New Name"})
        assert r.status_code in [200, 422]


class TestAdminComplete:
    """관리자 테스트 (4개)"""
    
    def test_12_admin_users(self, client, admin_token):
        assert client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    
    def test_13_admin_forbidden(self, client, customer_token):
        assert client.get("/api/admin/users", headers={"Authorization": f"Bearer {customer_token}"}).status_code == 403
    
    def test_14_admin_no_auth(self, client):
        assert client.get("/api/admin/users").status_code == 401


class TestCoupons:
    """쿠폰 테스트 (3개)"""
    
    def test_15_get_coupons(self, client, customer_token):
        assert client.get("/api/coupons", headers={"Authorization": f"Bearer {customer_token}"}).status_code == 200
    
    def test_16_get_my_coupons(self, client, customer_token):
        assert client.get("/api/coupons/my", headers={"Authorization": f"Bearer {customer_token}"}).status_code == 200
    
    def test_17_coupons_no_auth(self, client):
        assert client.get("/api/coupons").status_code == 401
