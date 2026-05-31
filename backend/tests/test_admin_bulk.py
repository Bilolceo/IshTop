"""
Tests for bulk action endpoints in admin router.
"""
import uuid
import pytest

from app.models import User, UserRole, Job


def test_bulk_activate_users(client, super_admin_token, test_db):
    users = []
    for _ in range(2):
        u = User(
            id=uuid.uuid4(),
            email=f"bulk_{uuid.uuid4().hex[:6]}@test.com",
            full_name="Test",
            role=UserRole.STUDENT,
            is_active_account=False,
            password_hash="x" * 60,
        )
        test_db.add(u)
        users.append(u)
    test_db.commit()

    response = client.post(
        "/api/v1/admin/users/bulk-action",
        json={"ids": [str(u.id) for u in users], "action": "activate"},
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["affected"] == 2


def test_bulk_deactivate_users(client, super_admin_token, test_db):
    users = []
    for _ in range(3):
        u = User(
            id=uuid.uuid4(),
            email=f"bulk_{uuid.uuid4().hex[:6]}@test.com",
            full_name="Test",
            role=UserRole.STUDENT,
            is_active_account=True,
            password_hash="x" * 60,
        )
        test_db.add(u)
        users.append(u)
    test_db.commit()

    response = client.post(
        "/api/v1/admin/users/bulk-action",
        json={"ids": [str(u.id) for u in users], "action": "deactivate"},
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["affected"] == 3


def test_bulk_action_users_invalid_action(client, super_admin_token):
    response = client.post(
        "/api/v1/admin/users/bulk-action",
        json={"ids": [str(uuid.uuid4())], "action": "delete"},
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert response.status_code == 400


def test_bulk_action_companies_verify(client, super_admin_token, test_db):
    companies = []
    for _ in range(2):
        c = User(
            id=uuid.uuid4(),
            email=f"comp_{uuid.uuid4().hex[:6]}@test.com",
            full_name="Company",
            role=UserRole.COMPANY,
            is_active_account=True,
            is_verified=False,
            password_hash="x" * 60,
        )
        test_db.add(c)
        companies.append(c)
    test_db.commit()

    response = client.post(
        "/api/v1/admin/companies/bulk-action",
        json={"ids": [str(c.id) for c in companies], "action": "verify"},
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["affected"] == 2
