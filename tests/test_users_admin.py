"""
Users and Admin Domain Tests
사용자 및 관리자 관련 엔드포인트 테스트
"""
import pytest
from datetime import date


class TestUsers:
    """사용자 테스트"""

    def test_get_my_profile(self, client, customer_token):
        """내 프로필 조회 테스트"""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == "customer@test.com"

    def test_update_my_profile(self, client, customer_token):
        """내 프로필 수정 테스트"""
        response = client.patch(
            "/users/me",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "name": "Updated Name",
                "address": "Updated Address"
            }
        )

        assert response.status_code == 200

        # 수정 확인
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["address"] == "Updated Address"

    def test_delete_my_account(self, client, customer_token):
        """계정 삭제 테스트"""
        response = client.delete(
            "/users/me",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200

    def test_unauthorized_access(self, client):
        """인증 없이 프로필 접근 실패 테스트"""
        response = client.get("/users/me")

        assert response.status_code == 401


class TestAdmin:
    """관리자 테스트"""

    def test_get_users_list_admin(self, client, admin_token, test_db):
        """관리자의 사용자 목록 조회 테스트"""
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["isSuccess"] is True
        payload = data["payload"]
        assert "content" in payload

    def test_get_users_list_customer_forbidden(self, client, customer_token):
        """고객의 사용자 목록 조회 실패 테스트 (권한 없음)"""
        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 403

    def test_update_user_role_admin(self, client, admin_token, test_db):
        """관리자의 사용자 역할 변경 테스트"""
        from app.models import User, UserRole, Gender
        from app.core.security import hash_password

        # 테스트용 사용자 생성
        user = User(
            email="roletest@test.com",
            password=hash_password("Password123!"),
            name="Role Test User",
            birth_date=date(1990, 1, 1),
            gender=Gender.MALE,
            address="Test Address",
            role=UserRole.CUSTOMER
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # 역할 변경
        response = client.patch(
            f"/api/admin/users/{user.id}/role",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"role": "SELLER"}
        )

        assert response.status_code == 200

    def test_get_statistics_admin(self, client, admin_token):
        """관리자의 통계 조회 테스트"""
        response = client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data or "isSuccess" in data

    def test_create_coupon_admin(self, client, admin_token):
        """관리자의 쿠폰 생성 테스트"""
        response = client.post(
            "/api/admin/coupons",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "code": "TESTCOUPON",
                "discount_type": "PERCENTAGE",
                "discount_value": 10,
                "min_order_amount": 10000,
                "max_discount_amount": 5000,
                "valid_from": "2025-01-01T00:00:00",
                "valid_until": "2025-12-31T23:59:59",
                "is_active": True
            }
        )

        assert response.status_code == 201
