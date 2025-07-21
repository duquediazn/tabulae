"""
This test module covers all endpoints in the /auth router.

TESTED ENDPOINTS:
[x] POST   /auth/register
[x] POST   /auth/login
[x] GET    /auth/profile
[x] POST   /auth/refresh
[x] POST   /auth/verify-password
[x] POST   /auth/logout
"""

import pytest
from app.models.user import User
from app.utils.authentication import hash_password
from sqlmodel import select
from app.tests.utils import (
    create_user_in_db,
    get_auth_headers,
    get_token_for_user,
)

register_data = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "testpass123",
}


@pytest.fixture()
def active_user(session):
    """Creates and returns an active user with default credentials."""
    user = create_user_in_db(
        session,
        name="Active User",
        email="active@example.com",
        password="testpass123",
        role="user",
        is_active=True,
    )
    return user


### TESTS ###


# POST   /auth/register
def test_register_user_success(client, session):
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    assert response.json()["email"] == register_data["email"]

    # Activate user for future login tests
    user = session.exec(
        select(User).where(User.email == register_data["email"])
    ).first()
    user.is_active = True
    session.add(user)
    session.commit()


def test_register_user_duplicate(client):
    client.post("/auth/register", json=register_data)  # create user
    response = client.post("/auth/register", json=register_data)  # duplicate
    assert response.status_code == 400


def test_register_missing_password(client):
    response = client.post(
        "/auth/register",
        json={"name": "User Without Password", "email": "new1@example.com"},
    )
    assert response.status_code == 422


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "password": "validpass123",
        },
    )
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Short Password",
            "email": "new2@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_register_short_name(client):
    response = client.post(
        "/auth/register",
        json={"name": "Al", "email": "new3@example.com", "password": "validpass123"},
    )
    assert response.status_code == 422


def test_register_invalid_role(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Wrong Role",
            "email": "new4@example.com",
            "password": "validpass123",
            "role": "superadmin",
        },
    )
    assert response.status_code == 422


# POST   /auth/login
def test_login_user(client, active_user):
    token = get_token_for_user(client, active_user.email, "testpass123")
    assert token is not None


def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "whateverpass"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_login_wrong_password(client, session):
    user = create_user_in_db(
        session,
        register_data["name"],
        register_data["email"],
        register_data["password"],
    )
    user.is_active = True
    session.add(user)
    session.commit()

    response = client.post(
        "/auth/login",
        data={"username": register_data["email"], "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client, session):
    # Create inactive user directly in DB
    inactive = create_user_in_db(
        session,
        name="Inactive User",
        email="inactive@example.com",
        password="validpass123",
        is_active=False,
    )

    response = client.post(
        "/auth/login",
        data={"username": inactive.email, "password": "validpass123"},
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_login_missing_fields(client):
    response = client.post("/auth/login", data={})
    assert response.status_code == 422


# GET    /auth/profile
def test_user_profile(client, active_user):
    token = get_token_for_user(client, active_user.email, "testpass123")
    headers = get_auth_headers(token)
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == active_user.email


def test_profile_no_token(client):
    response = client.get("/auth/profile")
    assert response.status_code == 401


def test_profile_invalid_token(client):
    # Fake but well-formed JWT
    fake_token = (
        "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9." "eyJzdWIiOiAiZmFrZSJ9.invalidsig"
    )
    headers = {"Authorization": f"Bearer {fake_token}"}
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_profile_deleted_user(client, session):
    user = create_user_in_db(
        session, "Ghost", "ghost@example.com", "ghostpass123", is_active=True
    )
    token = get_token_for_user(client, user.email, "ghostpass123")
    session.delete(user)
    session.commit()

    headers = get_auth_headers(token)
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_profile_inactive_user(client, session):
    user = create_user_in_db(
        session, "Inactive", "inactive2@example.com", "pass1234", is_active=True
    )
    token = get_token_for_user(client, user.email, "pass1234")

    user.is_active = False
    session.add(user)
    session.commit()

    headers = get_auth_headers(token)
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


# POST   /auth/refresh
def test_refresh_token(client, active_user):
    login_response = client.post(
        "/auth/login",
        data={"username": active_user.email, "password": "testpass123"},
    )
    assert login_response.status_code == 200
    cookies = login_response.cookies

    refresh_response = client.post("/auth/refresh", cookies=cookies)
    assert refresh_response.status_code == 200
    json_data = refresh_response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


def test_refresh_token_missing_cookie(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found in cookies."


def test_refresh_token_invalid_token(client):
    cookies = {"refresh_token": "invalid.token.value"}
    response = client.post("/auth/refresh", cookies=cookies)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_refresh_token_deleted_user(client, session):
    user = create_user_in_db(
        session, "Ghost", "ghost2@example.com", "ghostpass123", is_active=True
    )
    login_response = client.post(
        "/auth/login",
        data={"username": user.email, "password": "ghostpass123"},
    )
    refresh_cookie = login_response.cookies.get("refresh_token")
    session.delete(user)
    session.commit()

    response = client.post("/auth/refresh", cookies={"refresh_token": refresh_cookie})
    assert response.status_code == 401
    assert "not found" in response.json()["detail"].lower()


def test_refresh_token_inactive_user(client, session):
    user = create_user_in_db(
        session, "Inactive", "inactive3@example.com", "pass1234", is_active=True
    )
    login_response = client.post(
        "/auth/login",
        data={"username": user.email, "password": "pass1234"},
    )
    refresh_token = login_response.cookies.get("refresh_token")

    # Inactivate the user after login
    user.is_active = False
    session.add(user)
    session.commit()

    response = client.post("/auth/refresh", cookies={"refresh_token": refresh_token})
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


# POST   /auth/verify-password
def test_verify_password_success(client, active_user):
    token = get_token_for_user(client, active_user.email, "testpass123")
    headers = get_auth_headers(token)

    response = client.post(
        "/auth/verify-password",
        headers=headers,
        json={"password": "testpass123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password verified successfully"


def test_verify_password_no_token(client):
    response = client.post("/auth/verify-password", json={"password": "anypass"})
    assert response.status_code == 401


def test_verify_password_invalid_token(client):
    fake_token = (
        "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9." "eyJzdWIiOiAiZmFrZSJ9.invalidsig"
    )
    headers = {"Authorization": f"Bearer {fake_token}"}
    response = client.post(
        "/auth/verify-password",
        headers=headers,
        json={"password": "irrelevant"},
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_verify_password_inactive_user(client, session):
    user = create_user_in_db(
        session,
        "Inactive Verify",
        "inactive.verify@example.com",
        "verify123",
        is_active=True,
    )
    token = get_token_for_user(client, user.email, "verify123")

    # Inactivate user after getting token
    user.is_active = False
    session.add(user)
    session.commit()

    headers = get_auth_headers(token)
    response = client.post(
        "/auth/verify-password", headers=headers, json={"password": "verify123"}
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_verify_password_missing_field(client, active_user):
    token = get_token_for_user(client, active_user.email, "testpass123")
    headers = get_auth_headers(token)

    response = client.post("/auth/verify-password", headers=headers, json={})
    assert response.status_code == 422


def test_verify_password_failure(client, active_user):
    token = get_token_for_user(client, active_user.email, "testpass123")
    headers = get_auth_headers(token)

    response = client.post(
        "/auth/verify-password",
        headers=headers,
        json={"password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"


# POST   /auth/logout
def test_logout(client, active_user):
    login_response = client.post(
        "/auth/login",
        data={"username": active_user.email, "password": "testpass123"},
    )
    assert login_response.status_code == 200
    assert "set-cookie" in login_response.headers

    logout_response = client.post("/auth/logout", cookies=login_response.cookies)

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out successfully"
    assert "set-cookie" in logout_response.headers
    assert "Max-Age=0" in logout_response.headers["set-cookie"]


def test_logout_without_cookie(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_logout_always_sets_cookie_removal(client):
    response = client.post("/auth/logout")
    assert "set-cookie" in response.headers
    assert "Max-Age=0" in response.headers["set-cookie"]
