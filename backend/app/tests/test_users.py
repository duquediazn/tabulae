"""
This test module covers all endpoints in the /users router.

TESTED ENDPOINTS:
[x] POST   /users/
[x] GET    /users/
[x] GET    /users/{id}
[x] PUT    /users/{id}
[x] PUT    /users/bulk-status (bulk_update_user_status)
[x] DELETE /users/{id}
"""

import pytest
from app.tests.utils import (
    create_user_in_db,
    get_admin_headers,
    get_auth_headers,
    get_token_for_user,
)
from app.models.user import User
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.product_category import ProductCategory

### TESTS ###

# [x] POST   /users/
@pytest.mark.asyncio
async def test_admin_can_create_user(client, session):
    """Ensure an admin can create a new user successfully"""
    headers, _ = await get_admin_headers(client, session)

    new_user_data = {
        "name": "Nuevo Usuario",
        "email": "nuevo@example.com",
        "password": "pass1234",
        "role": "user",
        "is_active": True,
    }
    response = await client.post("/users/", json=new_user_data, headers=headers)

    assert response.headers["content-type"].startswith("application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_user_data["email"]
    assert data["name"] == new_user_data["name"]
    assert data["role"] == new_user_data["role"]
    assert "password" not in data

@pytest.mark.asyncio
async def test_admin_cannot_create_user_with_existing_email(client, session):
    """Ensure admin cannot create a user with an already existing email (bad request)"""
    headers, _ = await get_admin_headers(client, session)
    await create_user_in_db(session, "User A", "test@example.com", "pass")

    response = await client.post("/users/", json={
        "name": "New",
        "email": "test@example.com",
        "password": "pass1234",
        "role": "user",
        "is_active": True
    }, headers=headers)

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_regular_user_cannot_create_user(client, session):
    """Ensure a regular user cannot create a new user successfully (forbidden)"""
    user = await create_user_in_db(session, "Normal", "user@example.com", "pass")
    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    new_user_data = {
        "name": "Test",
        "email": "new@example.com",
        "password": "abc12345",
        "role": "user",
        "is_active": True,
    }
    response = await client.post("/users/", json=new_user_data, headers=headers)
    assert response.status_code == 403


# [x] GET    /users/

@pytest.mark.asyncio
async def test_admin_can_list_users(client, session):
    """Ensure admin can retrieve user list"""
    headers, _ = await get_admin_headers(client, session)
    await create_user_in_db(session, "Regular User", "user@example.com", "userpass")

    response = await client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_regular_user_cannot_list_users(client, session):
    """Ensure regular users cannot access the user list"""
    user = await create_user_in_db(session, "Regular User", "user@example.com", "userpass")
    token = await get_token_for_user(client, user.email, "userpass")
    headers = get_auth_headers(token)

    response = await client.get("/users/", headers=headers)
    assert response.status_code == 403


# [x] GET    /users/{id}
@pytest.mark.asyncio
async def test_admin_can_view_any_user(client, session):
    """Ensure admin can view any user's profile"""
    headers, _ = await get_admin_headers(client, session)
    target = await create_user_in_db(session, "User One", "user1@example.com", "pass")
    
    response = await client.get(f"/users/{target.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == target.email

@pytest.mark.asyncio
async def test_user_can_view_own_profile(client, session):
    """Ensure a user can view their own profile"""
    user = await create_user_in_db(session, "User", "user@example.com", "userpass")
    token = await get_token_for_user(client, user.email, "userpass")
    headers = get_auth_headers(token)

    response = await client.get(f"/users/{user.id}", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_user_cannot_view_other_user_profile(client, session):
    """Ensure a user cannot view another user's profile"""
    user1 = await create_user_in_db(session, "User1", "u1@example.com", "pass1")
    user2 = await create_user_in_db(session, "User2", "u2@example.com", "pass2")

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    response = await client.get(f"/users/{user2.id}", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()

# Pagitation testing
@pytest.mark.asyncio
async def test_user_list_pagination(client, session):
    """Ensure pagination works properly"""
    headers, _ = await get_admin_headers(client, session)
    for i in range(5):
        await create_user_in_db(session, f"User{i}", f"user{i}@example.com", "pass")

    response = await client.get("/users/?limit=2&offset=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["total"] >= 5


# [x] PUT    /users/{id}
@pytest.mark.asyncio
async def test_user_can_update_own_name(client, session):
    """Ensure a user can update their own name"""
    user = await create_user_in_db(session, "User One", "user1@example.com", "userpass1")
    token = await get_token_for_user(client, user.email, "userpass1")
    headers = get_auth_headers(token)

    response = await client.put(f"/users/{user.id}", json={"name": "Updated Name"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_user_cannot_update_other_user(client, session):
    """Ensure a suer cannot update another user profile (forbidden)"""
    user1 = await create_user_in_db(session, "User1", "u1@example.com", "pass1")
    user2 = await create_user_in_db(session, "User2", "u2@example.com", "pass2")

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    response = await client.put(f"/users/{user2.id}", json={"name": "Hacked"}, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_change_own_role(client, session):
    """Ensure a user can't change their own role (forbidden)"""
    user = await create_user_in_db(session, "User", "user@example.com", "userpass")
    token = await get_token_for_user(client, user.email, "userpass")
    headers = get_auth_headers(token)

    response = await client.put(f"/users/{user.id}", json={"role": "admin"}, headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_user_cannot_use_existing_email(client, session):
    """Ensure a user can't register an email that already exists (bad request)"""
    user1 = await create_user_in_db(session, "User1", "u1@example.com", "pass1")
    user2 = await create_user_in_db(session, "User2", "u2@example.com", "pass2")
    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    response = await client.put(f"/users/{user1.id}", json={"email": user2.email}, headers=headers)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_admin_can_update_other_user(client, session):
    """Ensure admin can update another user's full profile"""
    headers, admin = await get_admin_headers(client, session)
    user = await create_user_in_db(session, "Target", "target@example.com", "targetpass")

    update_data = {
        "name": "Modified Name",
        "email": "modified@example.com",
        "role": "admin",
        "is_active": False,
        "password": "newpass123",
    }
    response = await client.put(f"/users/{user.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["role"] == update_data["role"]
    assert data["is_active"] is False

@pytest.mark.asyncio
async def test_admin_update_nonexistent_user_returns_404(client, session):
    """Ensure admin cannot update a non-existent user (Not found)"""
    headers, _ = await get_admin_headers(client, session)
    response = await client.put("/users/9999", json={"name": "Ghost"}, headers=headers)
    assert response.status_code == 404

# [x] PUT    /users/bulk-status (bulk_update_user_status)
@pytest.mark.asyncio
async def test_admin_can_bulk_update_user_status(client, session):
    """Ensure admin can bulk deactivate users (skipping self and already inactive)"""
    headers, admin = await get_admin_headers(client, session)

    user1 = await create_user_in_db(session, "User A", "a@example.com", "pass", is_active=True)
    user2 = await create_user_in_db(session, "User B", "b@example.com", "pass", is_active=True)
    user3 = await create_user_in_db(session, "User C", "c@example.com", "pass", is_active=False)

    response = await client.put(
        "/users/bulk-status",
        json={"ids": [admin.id, user1.id, user2.id, user3.id], "is_active": False},
        headers=headers,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "2 users updated"
    assert result["skipped"] == 2

    # Confirm in DB
    for user_id in [user1.id, user2.id, user3.id]:
        obj = await session.get(User, user_id)
        assert obj.is_active is False

@pytest.mark.asyncio
async def test_regular_user_cannot_bulk_update_users(client, session):
    """Ensure non-admin users cannot perform bulk status update"""
    user = await create_user_in_db(session, "User D", "d@example.com", "pass")
    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = await client.put(
        "/users/bulk-status",
        json={"ids": [user.id], "is_active": True},
        headers=headers,
    )
    assert response.status_code == 403


# [x] DELETE /users/{id}
@pytest.mark.asyncio
async def test_admin_can_delete_user_without_movements(client, session):
    """ Ensure admin can delete a user with no stock movements"""
    headers, _ = await get_admin_headers(client, session)

    user = await create_user_in_db(session, "User Clean", "clean@example.com", "pass")

    response = await client.delete(f"/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user.email


@pytest.mark.asyncio
async def test_admin_cannot_delete_user_with_movements(client, session):
    """Ensure admin cannot delete a user who has stock movements"""
    session.add(ProductCategory(id=1, name="Test Category"))
    session.add(Warehouse(id=1, name="WH1"))
    await session.commit()
    session.add(Product(id=1, sku="SKU001", short_name="TestProd", description="Test", category_id=1))
    await session.commit()

    headers, _ = await get_admin_headers(client, session)
    user = await create_user_in_db(session, "User Dirty", "dirty@example.com", "pass")

    # Create stock movement
    move = StockMove(move_type="incoming", user_id=user.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)
    session.add(StockMoveLine(move_id=move.id, line_id=1, warehouse_id=1, product_id=1, lot="NO_LOT", expiration_date=None, quantity=1))
    await session.commit()

    response = await client.delete(f"/users/{user.id}", headers=headers)
    assert response.status_code == 400
    assert "movements" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_cannot_delete_nonexistent_user(client, session):
    """Ensure deleting a non-existent user returns 404"""
    headers, _ = await get_admin_headers(client, session)
    response = await client.delete("/users/9999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_self(client, session):
    """Ensure a regular user cannot delete their own profile (forbidden)"""
    user = await create_user_in_db(session, "Selfy", "self@example.com", "pass")
    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = await client.delete(f"/users/{user.id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_regular_user_cannot_delete_other_user(client, session):
    """Ensure regular users cannot delete other users"""
    headers, admin = await get_admin_headers(client, session)
    user = await create_user_in_db(session, "Regular", "regular@example.com", "pass")

    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)
    response = await client.delete(f"/users/{admin.id}", headers=headers)
    assert response.status_code == 403
