# This file contains reusable helper functions for testing authentication.

from app.utils.authentication import hash_password
from app.models.user import User


def create_user_in_db(session, name, email, password, role="user", is_active=True):
    """Inserts a user directly into the test database."""
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_token_for_user(client, email, password):
    """ Logs in a user and returns the access token."""
    response = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def get_auth_headers(token):
    """Builds the Authorization header with a Bearer token."""
    return {"Authorization": f"Bearer {token}"}


def get_admin_headers(client, session, email="admin@example.com", password="adminpass"):
    """
    Creates an admin user in the test DB and returns auth headers.
    """
    admin = create_user_in_db(session, "Admin", email, password, role="admin")
    token = get_token_for_user(client, email, password)
    return get_auth_headers(token), admin
