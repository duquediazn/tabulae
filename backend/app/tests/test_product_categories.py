"""
This test module covers all endpoints in the /categories router.

TESTED ENDPOINTS:
[X] GET   /categories/
[X] POST   /categories/
[X] PUT    /categories/{id}
[X] DELETE    /categories/{id}
"""

from sqlmodel import delete
import pytest
from app.tests.utils import (
    create_user_in_db,
    get_admin_headers,
    get_auth_headers,
    get_token_for_user,
)
from app.models.product import Product


### TESTS ###

#[] GET   /categories/
def test_admin_can_get_all_categories(client, session):
    """Ensure admin can list all categories."""
    headers, _ = get_admin_headers(client, session)

    response = client.get("/categories/", headers=headers)

    data = response.json()
    
    assert "data" in data
    assert isinstance(data["data"], list)
    assert response.status_code == 200

def test_user_can_get_all_categories(client, session):
    """Ensure a regular user can list all categories"""
    user = create_user_in_db(session, "test_user", "test_user@email.com", "user_password", role="user", is_active=True)
    token = get_token_for_user(client, "test_user@email.com", "user_password")
    headers = get_auth_headers(token)

    response = client.get("/categories/", headers=headers)

    data = response.json()
    
    assert "data" in data
    assert isinstance(data["data"], list)
    assert response.status_code == 200

def test_category_list_pagination(client, session):
    """Ensure pagination works properly"""
    headers, _ = get_admin_headers(client, session)
    for i in range(5):
        client.post("/categories/", json={"name": f"cat_{i}"}, headers=headers)

    response = client.get("/categories/?limit=2&offset=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["total"] >= 5


#[] POST   /categories/
def test_admin_can_create_category(client, session):
    """Ensure an admin can create a new category successfully"""
    headers, _ = get_admin_headers(client, session)

    new_category = {"name": "admin_category"}

    response = client.post("/categories/", json=new_category, headers=headers)

    assert response.headers["content-type"].startswith("application/json")
    assert response.status_code == 201

def test_admin_cannot_create_duplicated_category(client, session):
    """Ensure admin cannot create a duplicated category (bad request)"""
    headers, _ = get_admin_headers(client, session)

    new_category = {"name": "duplicated_category"}

    # First creation
    response = client.post("/categories/", json=new_category, headers=headers)
    assert response.status_code == 201

    # Second attempt
    response = client.post("/categories/", json=new_category, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_user_cannot_create_category(client, session):
    """Ensure an role user cannot create a new category successfully (forbidden)"""
    user = create_user_in_db(session, "test_user", "test_user@email.com", "user_password", role="user", is_active=True)
    token = get_token_for_user(client, "test_user@email.com", "user_password")
    headers = get_auth_headers(token)

    new_category = {"name": "user_category"}

    response = client.post("/categories/", json=new_category, headers=headers)

    assert response.headers["content-type"].startswith("application/json")
    assert response.status_code == 403

def test_admin_cannot_create_category_with_short_name(client, session):
    """Ensure admin cannot create a category with a name that is too short"""
    headers, _ = get_admin_headers(client, session)

    response = client.post("/categories/", json={"name": "ab"}, headers=headers)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("at least 3 characters" in err["msg"] for err in detail)


def test_admin_cannot_create_category_with_too_long_name(client, session):
    """Ensure admin cannot create a category with a name that is too long"""
    headers, _ = get_admin_headers(client, session)
    long_name = "a" * 51

    response = client.post("/categories/", json={"name": long_name}, headers=headers)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("at most 50 characters" in err["msg"] for err in detail)


# [] PUT    /categories/{id}
def test_admin_can_update_category(client, session):
    """Ensure admin can update an existing category."""
    headers, _ = get_admin_headers(client, session)

    new_category = {"name": "new_category"}
    updated_category = {"name": "update_category"}

    # Category creation
    response = client.post("/categories/", json=new_category, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    # Category update
    response = client.put(f"/categories/{category_id}", json=updated_category, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Update_category"

def test_admin_cannot_update_category_with_short_name(client, session):
    """Ensure admin cannot update category with too short a name (validation error)"""
    headers, _ = get_admin_headers(client, session)

    # Create valid category
    response = client.post("/categories/", json={"name": "valid_name"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    # Try to update to a too short name
    response = client.put(
        f"/categories/{category_id}",
        json={"name": "ab"},
        headers=headers,
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("at least 3 characters" in err["msg"] for err in detail)

def test_admin_cannot_update_category_with_too_long_name(client, session):
    """Ensure admin cannot update category with too long a name (validation error)"""
    headers, _ = get_admin_headers(client, session)

    # Crate valid cateogry
    response = client.post("/categories/", json={"name": "valid_name"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    long_name = "a" * 51
    response = client.put(
        f"/categories/{category_id}",
        json={"name": long_name},
        headers=headers,
    )
    assert response.status_code == 422
    assert any("at most 50 characters" in err["msg"] for err in response.json()["detail"])


def test_admin_cannot_update_category_to_existing_name(client, session):
    """Ensure admin cannot rename a category to a name that already exists (conflict)"""
    headers, _ = get_admin_headers(client, session)

    # Create 2 categories
    response = client.post("/categories/", json={"name": "category_a"}, headers=headers)
    assert response.status_code == 201
    id_a = response.json()["id"]

    response = client.post("/categories/", json={"name": "category_b"}, headers=headers)
    assert response.status_code == 201
    id_b = response.json()["id"]

    # Try to rename B to A
    response = client.put(f"/categories/{id_b}", json={"name": "category_a"}, headers=headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_admin_cannot_update_nonexistent_category(client, session):
    """Ensure admin receives 404 when updating a non-existent category"""
    headers, _ = get_admin_headers(client, session)

    response = client.put("/categories/9999", json={"name": "newname"}, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_user_cannot_update_category(client, session):
    """Ensure regular user cannot update any category (forbidden)"""
    headers, _ = get_admin_headers(client, session)
    response = client.post("/categories/", json={"name": "editable"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    user = create_user_in_db(session, "Regular", "user@email.com", "pass", role="user")
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.put(f"/categories/{category_id}", json={"name": "blocked"}, headers=headers)
    assert response.status_code == 403


# [] DELETE    /categories/{id}
def test_admin_can_delete_category_without_products(client, session):
    """Ensure admin can delete a category that has no products"""
    headers, _ = get_admin_headers(client, session)

    response = client.post("/categories/", json={"name": "to_delete"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    response = client.delete(f"/categories/{category_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == category_id


def test_admin_cannot_delete_category_with_products(client, session):
    """Ensure admin cannot delete a category that has associated products"""
    headers, _ = get_admin_headers(client, session)

    # Create category
    response = client.post("/categories/", json={"name": "linked_cat"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    # Insert product associated with category
    product = Product(
        sku="SKU1",
        short_name="Product 1",
        description="Linked product",
        category_id=category_id,
    )
    session.add(product)
    session.commit()

    # Try to delete category
    response = client.delete(f"/categories/{category_id}", headers=headers)
    assert response.status_code == 400
    assert "associated products" in response.json()["detail"].lower()


def test_admin_cannot_delete_nonexistent_category(client, session):
    """Ensure deleting a non-existent category returns 404"""
    headers, _ = get_admin_headers(client, session)

    response = client.delete("/categories/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_user_cannot_delete_category(client, session):
    """Ensure a regular user cannot delete categories (forbidden)"""
    headers, _ = get_admin_headers(client, session)
    response = client.post("/categories/", json={"name": "protected"}, headers=headers)
    assert response.status_code == 201, response.json()
    category_id = response.json()["id"]

    user = create_user_in_db(session, "Regular", "user@email.com", "pass", role="user")
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.delete(f"/categories/{category_id}", headers=headers)
    assert response.status_code == 403
