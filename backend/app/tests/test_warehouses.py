"""
This test module covers all endpoints in the /warehouses router.

TESTED ENDPOINTS:
[X] POST   /warehouses/
[X] GET    /warehouses/
[X] GET    /warehouses/{id}
[X] PUT    /warehouses/{id}
[X] PUT    /warehouses/bulk-active
[X] DELETE /warehouses/{id}
"""

from app.models.product_category import ProductCategory
from app.models.product import Product
from app.models.stock_move import StockMove
import pytest
from sqlmodel import select
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.models.stock_move_line import StockMoveLine
from app.tests.utils import (
    create_user_in_db,
    get_admin_headers,
    get_auth_headers,
    get_token_for_user,
)

# [X] POST   /warehouses/
def test_admin_can_create_warehouse(client, session):
    """Ensure an admin can create a new warehouse successfully"""
    headers, _ = get_admin_headers(client, session)

    new_warehouse = {"description": "Central Depot", "is_active": True}

    response = client.post("/warehouses/", json=new_warehouse, headers=headers)

    assert response.status_code == 201
    assert response.headers["content-type"].startswith("application/json")
    
    data = response.json()
    assert data["description"] == new_warehouse["description"]
    assert data["is_active"] is True
    assert "id" in data


def test_user_cannot_create_warehouse(client, session):
    """Ensure regular users cannot create warehouses (forbidden)"""
    user = create_user_in_db(session, "User", "user@example.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse_data = {"description": "Unauthorized Warehouse"}

    response = client.post("/warehouses/", json=warehouse_data, headers=headers)

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_admin_cannot_create_warehouse_with_missing_description(client, session):
    """Ensure warehouse creation fails if 'description' is missing"""
    headers, _ = get_admin_headers(client, session)

    response = client.post("/warehouses/", json={}, headers=headers)

    assert response.status_code == 422
    assert any(err["loc"][-1] == "description" for err in response.json()["detail"])


def test_admin_cannot_create_warehouse_with_long_description(client, session):
    """Ensure warehouse description cannot exceed 255 characters"""
    headers, _ = get_admin_headers(client, session)

    long_description = "X" * 256
    payload = {"description": long_description}

    response = client.post("/warehouses/", json=payload, headers=headers)

    assert response.status_code == 422
    assert any("at most 255 characters" in err["msg"] for err in response.json()["detail"])


# [X] GET    /warehouses/

def test_admin_can_list_all_warehouses(client, session):
    """Ensure admin can list all warehouses"""
    headers, _ = get_admin_headers(client, session)

    session.add_all([
        Warehouse(description="WH A", is_active=True),
        Warehouse(description="WH B", is_active=False),
    ])
    session.commit()

    response = client.get("/warehouses/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["data"]) == 2


def test_user_can_filter_only_active_warehouses(client, session):
    """Ensure regular user sees only active warehouses when using is_active=true"""
    user = create_user_in_db(session, "User", "u@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    session.add_all([
        Warehouse(description="WH Visible", is_active=True),
        Warehouse(description="WH Hidden", is_active=False),
    ])
    session.commit()

    response = client.get("/warehouses/?is_active=true", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["description"] == "WH Visible"


def test_warehouse_list_pagination_works(client, session):
    """Ensure pagination works properly with limit and offset"""
    headers, _ = get_admin_headers(client, session)

    for i in range(5):
        session.add(Warehouse(description=f"WH {i}"))
    session.commit()

    response = client.get("/warehouses/?limit=2&offset=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["data"]) == 2


def test_warehouse_list_filter_by_search_and_is_active(client, session):
    """Ensure filtering by search term and is_active works"""
    headers, _ = get_admin_headers(client, session)

    session.add_all([
        Warehouse(description="Main Warehouse", is_active=True),
        Warehouse(description="Backup WH", is_active=False),
        Warehouse(description="MAIN Depot", is_active=True),
    ])
    session.commit()

    # Search "main", should match two
    resp = client.get("/warehouses/?search=main", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    # Filter by is_active = false
    resp = client.get("/warehouses/?is_active=false", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["data"][0]["is_active"] is False


# [X] GET    /warehouses/{id}

def test_admin_can_view_any_warehouse(client, session):
    """Ensure admin can view any warehouse (active or not)"""
    headers, _ = get_admin_headers(client, session)

    warehouse = Warehouse(description="Hidden WH", is_active=False)
    session.add(warehouse)
    session.commit()

    response = client.get(f"/warehouses/{warehouse.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == warehouse.description

def test_user_can_view_active_warehouse(client, session):
    """Ensure regular user can view active warehouse"""
    user = create_user_in_db(session, "User", "u@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse = Warehouse(description="Public WH", is_active=True)
    session.add(warehouse)
    session.commit()

    response = client.get(f"/warehouses/{warehouse.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == warehouse.description

def test_user_cannot_view_inactive_warehouse(client, session):
    """Ensure regular user cannot view an inactive warehouse"""
    user = create_user_in_db(session, "User", "user@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse = Warehouse(description="Hidden WH", is_active=False)
    session.add(warehouse)
    session.commit()

    response = client.get(f"/warehouses/{warehouse.id}", headers=headers)
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()

def test_get_nonexistent_warehouse_returns_404(client, session):
    """Ensure getting a non-existent warehouse returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.get("/warehouses/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# [X] PUT    /warehouses/{id}

def test_admin_can_update_warehouse_description(client, session):
    """Ensure admin can update the description of a warehouse"""
    headers, _ = get_admin_headers(client, session)
    warehouse = Warehouse(description="Old Description", is_active=True)
    session.add(warehouse)
    session.commit()

    update = {"description": "Updated Description"}

    response = client.put(f"/warehouses/{warehouse.id}", json=update, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update["description"]
    assert data["is_active"] is True

def test_admin_can_deactivate_warehouse_without_stock(client, session):
    """Ensure admin can deactivate a warehouse if it has no stock"""
    headers, _ = get_admin_headers(client, session)
    warehouse = Warehouse(description="Empty WH", is_active=True)
    session.add(warehouse)
    session.commit()

    update = {"is_active": False}

    response = client.put(f"/warehouses/{warehouse.id}", json=update, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False

def test_admin_cannot_deactivate_warehouse_with_stock(client, session):
    """Ensure admin cannot deactivate a warehouse that has stock"""
    headers, _ = get_admin_headers(client, session)

    # Crear categoría y producto
    session.add(ProductCategory(id=1, name="TestCat"))
    session.commit()

    product = Product(id=1, sku="TEST001", short_name="TestProd", category_id=1)
    session.add(product)
    session.commit()

    # Crear almacén
    warehouse = Warehouse(id=1, description="With Stock", is_active=True)
    session.add(warehouse)
    session.commit()

    # Añadir stock
    stock = Stock(product_id=1, warehouse_id=1, lot="NO_LOT", quantity=10)
    session.add(stock)
    session.commit()

    # Intentar desactivarlo
    response = client.put(f"/warehouses/{warehouse.id}", json={"is_active": False}, headers=headers)

    assert response.status_code == 403
    assert "cannot be deactivated" in response.json()["detail"].lower()


def test_update_nonexistent_warehouse_returns_404(client, session):
    """Ensure updating a non-existent warehouse returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.put("/warehouses/9999", json={"description": "X"}, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_user_cannot_update_warehouse(client, session):
    """Ensure regular user cannot update a warehouse"""
    user = create_user_in_db(session, "User", "user@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse = Warehouse(description="Editable", is_active=True)
    session.add(warehouse)
    session.commit()

    response = client.put(f"/warehouses/{warehouse.id}", json={"description": "Hacked"}, headers=headers)
    assert response.status_code == 403

def test_admin_cannot_update_warehouse_with_long_description(client, session):
    """Ensure description longer than 255 chars triggers validation error"""
    headers, _ = get_admin_headers(client, session)

    warehouse = Warehouse(description="Short", is_active=True)
    session.add(warehouse)
    session.commit()

    long_text = "X" * 256
    response = client.put(f"/warehouses/{warehouse.id}", json={"description": long_text}, headers=headers)

    assert response.status_code == 422
    assert any("at most 255 characters" in err["msg"] for err in response.json()["detail"])


# [X] PUT    /warehouses/bulk-active

def test_admin_can_bulk_deactivate_warehouses_without_stock(client, session):
    """Ensure admin can deactivate multiple warehouses if they have no stock"""
    headers, _ = get_admin_headers(client, session)

    w1 = Warehouse(description="WH1", is_active=True)
    w2 = Warehouse(description="WH2", is_active=True)
    session.add_all([w1, w2])
    session.commit()

    response = client.put(
        "/warehouses/bulk-active",
        json={"ids": [w1.id, w2.id], "is_active": False},
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "2 warehouses updated"
    assert result["skipped"] == 0

    for wid in [w1.id, w2.id]:
        assert session.get(Warehouse, wid).is_active is False

def test_admin_cannot_bulk_deactivate_warehouse_with_stock(client, session):
    """Ensure warehouses with stock are skipped during bulk deactivation"""
    headers, _ = get_admin_headers(client, session)

    # Crear categoría y producto
    category = ProductCategory(name="BulkCat")
    session.add(category)
    session.commit()

    product = Product(sku="BULKSKU", short_name="BulkProd", category_id=category.id)
    session.add(product)
    session.commit()

    # WH1 con stock, WH2 sin stock
    wh1 = Warehouse(description="With Stock", is_active=True)
    wh2 = Warehouse(description="Empty", is_active=True)
    session.add_all([wh1, wh2])
    session.commit()

    stock = Stock(product_id=product.id, warehouse_id=wh1.id, lot="NO_LOT", quantity=10)
    session.add(stock)
    session.commit()

    response = client.put(
        "/warehouses/bulk-active",
        json={"ids": [wh1.id, wh2.id], "is_active": False},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "1 warehouses updated"
    assert data["skipped"] == 1
    assert session.get(Warehouse, wh1.id).is_active is True
    assert session.get(Warehouse, wh2.id).is_active is False

def test_user_cannot_bulk_update_warehouses(client, session):
    """Ensure non-admin users cannot use bulk-active endpoint"""
    user = create_user_in_db(session, "User", "u@example.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    wh = Warehouse(description="Blocked", is_active=True)
    session.add(wh)
    session.commit()

    response = client.put(
        "/warehouses/bulk-active",
        json={"ids": [wh.id], "is_active": False},
        headers=headers,
    )
    assert response.status_code == 403


# [X] DELETE /warehouses/{id}

def test_admin_can_delete_warehouse_without_movements(client, session):
    """Ensure admin can delete a warehouse without stock movements"""
    headers, _ = get_admin_headers(client, session)

    wh = Warehouse(description="To Delete", is_active=True)
    session.add(wh)
    session.commit()

    response = client.delete(f"/warehouses/{wh.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == wh.id
    assert session.get(Warehouse, wh.id) is None

def test_admin_cannot_delete_warehouse_with_movements(client, session):
    """Ensure admin cannot delete a warehouse with associated stock movements"""
    headers, admin = get_admin_headers(client, session)

    # Crear categoría, producto, almacén
    session.add(ProductCategory(id=1, name="Locked"))
    session.commit()

    session.add(Product(id=1, sku="SKUDEL", short_name="Prod", category_id=1))
    session.commit()

    wh = Warehouse(id=1, description="With Movement", is_active=True)
    session.add(wh)
    session.commit()

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    line = StockMoveLine(
        move_id=move.move_id,
        line_id=1,
        warehouse_id=wh.id,
        product_id=1,
        lot="NO_LOT",
        expiration_date=None,
        quantity=5
    )
    session.add(line)
    session.commit()

    response = client.delete(f"/warehouses/{wh.id}", headers=headers)
    assert response.status_code == 400
    assert "movements" in response.json()["detail"].lower()

def test_admin_cannot_delete_nonexistent_warehouse(client, session):
    """Ensure deleting a non-existent warehouse returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.delete("/warehouses/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_user_cannot_delete_warehouse(client, session):
    """Ensure regular users cannot delete warehouses"""
    user = create_user_in_db(session, "User", "user@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    wh = Warehouse(description="Protected", is_active=True)
    session.add(wh)
    session.commit()

    response = client.delete(f"/warehouses/{wh.id}", headers=headers)
    assert response.status_code == 403
