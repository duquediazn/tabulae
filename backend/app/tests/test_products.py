"""
This test module covers all endpoints in the /products router.

TESTED ENDPOINTS:
[X] GET    /products/
[X] GET    /products/{id}
[X] POST   /products/
[X] PUT    /products/{id}
[X] PUT    /products/bulk-status
[X] DELETE /products/{id}
"""

from app.utils.validation import normalize_category
import pytest
from app.models.product import Product
from app.models.stock import Stock
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.models.product_category import ProductCategory
from app.tests.utils import (
    create_user_in_db,
    get_admin_headers,
    get_auth_headers,
    get_token_for_user,
)


### TESTS ###
# [X] GET    /products/
def test_admin_can_list_all_products(client, session):
    """Ensure admin can list all products (active and inactive)"""
    headers, _ = get_admin_headers(client, session)

    # Create category and products
    category = ProductCategory(name=normalize_category("TestCat"))
    session.add(category)
    session.commit()

    session.add_all([
        Product(sku="SKU1", short_name="Prod A", description="Test", category_id=category.id, is_active=True),
        Product(sku="SKU2", short_name="Prod B", description="Test", category_id=category.id, is_active=False),
    ])
    session.commit()

    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert any(p["sku"] == "SKU1" for p in data["data"])
    assert any(p["sku"] == "SKU2" for p in data["data"])


def test_user_sees_only_active_products(client, session):
    """Ensure regular user only sees active products"""
    # Setup data
    category = ProductCategory(name=normalize_category("TestCat"))
    session.add(category)
    session.commit()
    session.add_all([
        Product(sku="SKU3", short_name="Visible", category_id=category.id, is_active=True),
        Product(sku="SKU4", short_name="Hidden", category_id=category.id, is_active=False),
    ])
    session.commit()

    user = create_user_in_db(session, "user", "user@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["sku"] == "SKU3"


def test_pagination_works_on_product_list(client, session):
    """Ensure pagination (limit & offset) works properly"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name=normalize_category("CatOne"))
    session.add(category)
    session.commit()

    for i in range(5):
        session.add(Product(sku=f"SKU{i}", short_name=f"Product {i}", category_id=category.id))
    session.commit()

    response = client.get("/products/?limit=2&offset=1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["data"]) == 2


def test_search_filters_by_name_or_sku(client, session):
    """Ensure search by short_name or SKU works (case-insensitive)"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name=normalize_category("SearchCat"))
    session.add(category)
    session.commit()

    session.add_all([
        Product(sku="TEST123", short_name="Alpha Product", category_id=category.id),
        Product(sku="ZZZ999", short_name="Beta Product", category_id=category.id),
    ])
    session.commit()

    resp = client.get("/products/?search=alpha", headers=headers)
    assert resp.status_code == 200
    results = resp.json()["data"]
    assert len(results) == 1
    assert results[0]["short_name"] == "Alpha Product"

    resp = client.get("/products/?search=zzz", headers=headers)
    assert resp.status_code == 200
    results = resp.json()["data"]
    assert len(results) == 1
    assert results[0]["sku"] == "ZZZ999"

def test_filter_by_category_id(client, session):
    """Ensure products can be filtered by category ID"""
    headers, _ = get_admin_headers(client, session)

    cat1 = ProductCategory(name=normalize_category("CatOne"))
    cat2 = ProductCategory(name=normalize_category("CatTwo"))
    session.add_all([cat1, cat2])
    session.commit()

    session.add_all([
        Product(sku="SKU101", short_name="ProdOne", category_id=cat1.id),
        Product(sku="SKU102", short_name="ProdTwo", category_id=cat2.id),
    ])
    session.commit()

    resp = client.get(f"/products/?category_id={cat1.id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 1
    expected_name = normalize_category("CatOne")
    assert data["data"][0]["category_name"] == expected_name


def test_admin_can_filter_by_is_active(client, session):
    """Ensure admin can filter products by is_active status"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name=normalize_category("ActFilter"))
    session.add(category)
    session.commit()

    session.add_all([
        Product(sku="ACTIVE01", short_name="Active P", category_id=category.id, is_active=True),
        Product(sku="INACTIVE01", short_name="Inactive P", category_id=category.id, is_active=False),
    ])
    session.commit()

    resp = client.get("/products/?is_active=true", headers=headers)
    assert resp.status_code == 200
    skus = [p["sku"] for p in resp.json()["data"]]
    assert "ACTIVE01" in skus
    assert "INACTIVE01" not in skus

    resp = client.get("/products/?is_active=false", headers=headers)
    assert resp.status_code == 200
    skus = [p["sku"] for p in resp.json()["data"]]
    assert "INACTIVE01" in skus
    assert "ACTIVE01" not in skus


def test_user_cannot_filter_by_is_active(client, session):
    """Ensure regular users always get only active products, even if using is_active param"""
    category = ProductCategory(name=normalize_category("UserView"))
    session.add(category)
    session.commit()

    session.add_all([
        Product(sku="VISIBLE1", short_name="Visible", category_id=category.id, is_active=True),
        Product(sku="HIDDEN1", short_name="Hidden", category_id=category.id, is_active=False),
    ])
    session.commit()

    user = create_user_in_db(session, "user", "u@email.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    resp = client.get("/products/?is_active=false", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["sku"] == "VISIBLE1"

# [X] GET    /products/{id}
def test_admin_can_view_any_product(client, session):
    """Ensure admin can view any product (active or not)"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name=normalize_category("AdminView"))
    session.add(category)
    session.commit()

    product = Product(sku="ADM001", short_name="Hidden Product", category_id=category.id, is_active=False)
    session.add(product)
    session.commit()

    response = client.get(f"/products/{product.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["sku"] == "ADM001"


def test_user_can_view_active_product(client, session):
    """Ensure regular user can view active product"""
    category = ProductCategory(name=normalize_category("UserView"))
    session.add(category)
    session.commit()

    product = Product(sku="USR001", short_name="Visible", category_id=category.id, is_active=True)
    session.add(product)
    session.commit()

    user = create_user_in_db(session, "user", "user@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.get(f"/products/{product.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["sku"] == "USR001"


def test_user_cannot_view_inactive_product(client, session):
    """Ensure regular user cannot view an inactive product (403)"""
    category = ProductCategory(name=normalize_category("PrivateCat"))
    session.add(category)
    session.commit()

    product = Product(sku="PRV001", short_name="Private", category_id=category.id, is_active=False)
    session.add(product)
    session.commit()

    user = create_user_in_db(session, "user", "user@z.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.get(f"/products/{product.id}", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_get_nonexistent_product_returns_404(client, session):
    """Ensure getting a non-existent product returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.get("/products/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# [X] POST   /products/
def test_admin_can_create_product_successfully(client, session):
    """Ensure admin can create a new product"""
    headers, _ = get_admin_headers(client, session)
    # Create category first (normalized)
    category = ProductCategory(name="Electronics")
    session.add(category)
    session.commit()

    product_data = {
        "sku": "PROD001",
        "short_name": "Smartphone",
        "description": "A high-end phone",
        "category_id": category.id
    }

    response = client.post("/products/", json=product_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "PROD001"
    assert data["short_name"] == "Smartphone"
    assert data["category_id"] == category.id
    assert data["category_name"] == category.name


def test_admin_cannot_create_duplicate_sku(client, session):
    """Ensure admin cannot create a product with an existing SKU"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name="Books")
    session.add(category)
    session.commit()

    product = Product(sku="BOOK123", short_name="Book", category_id=category.id)
    session.add(product)
    session.commit()

    product_data = {
        "sku": "BOOK123",
        "short_name": "Duplicate Book",
        "description": "Conflict SKU",
        "category_id": category.id
    }

    response = client.post("/products/", json=product_data, headers=headers)
    assert response.status_code == 400
    assert "sku" in response.json()["detail"].lower()


def test_admin_cannot_create_product_with_invalid_category(client, session):
    """Ensure admin cannot create product with non-existent category"""
    headers, _ = get_admin_headers(client, session)

    product_data = {
        "sku": "BADCAT1",
        "short_name": "NoCat",
        "description": "Invalid category",
        "category_id": 9999  # not created
    }

    response = client.post("/products/", json=product_data, headers=headers)
    assert response.status_code == 400
    assert "category" in response.json()["detail"].lower()


def test_user_cannot_create_product(client, session):
    """Ensure regular users cannot create products (forbidden)"""
    user = create_user_in_db(session, "Regular", "user@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    category = ProductCategory(name="CatUser")
    session.add(category)
    session.commit()

    product_data = {
        "sku": "USRPROD1",
        "short_name": "Unauthorized",
        "description": "Should be forbidden",
        "category_id": category.id
    }

    response = client.post("/products/", json=product_data, headers=headers)
    assert response.status_code == 403


def test_admin_cannot_create_product_with_invalid_data(client, session):
    """Ensure invalid product data triggers validation error (422)"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name="InvalidData")
    session.add(category)
    session.commit()

    bad_data = {
        "sku": "ab",  # too short and lowercase
        "short_name": "No",  # too short
        "category_id": category.id
    }

    response = client.post("/products/", json=bad_data, headers=headers)
    assert response.status_code == 422

# [X] PUT    /products/{id}
def test_user_can_update_product_fields_except_is_active(client, session):
    """Ensure user can update name/sku/category, but not is_active"""
    category1 = ProductCategory(name="Cat1")
    category2 = ProductCategory(name="Cat2")
    session.add_all([category1, category2])
    session.commit()

    product = Product(sku="UPD123", short_name="Original", description="Old", category_id=category1.id)
    session.add(product)
    session.commit()

    user = create_user_in_db(session, "User", "u@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    update_data = {
        "sku": "UPD999",
        "short_name": "NewName",
        "description": "Updated",
        "category_id": category2.id
    }

    response = client.put(f"/products/{product.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "UPD999"
    assert data["short_name"] == "NewName"
    assert data["description"] == "Updated"
    assert data["category_id"] == category2.id


def test_admin_can_update_all_fields_in_product(client, session):
    """Ensure admin can update all fields including is_active"""
    headers, _ = get_admin_headers(client, session)
    cat = ProductCategory(name="AdminCat")
    session.add(cat)
    session.commit()

    product = Product(sku="ADMIN1", short_name="Editable", category_id=cat.id)
    session.add(product)
    session.commit()

    update = {
        "sku": "ADMIN2",
        "short_name": "Updated Admin",
        "description": "Admin edit",
        "is_active": False
    }

    response = client.put(f"/products/{product.id}", json=update, headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_user_cannot_change_product_is_active(client, session):
    """Ensure user cannot change is_active field (forbidden)"""
    category = ProductCategory(name="RestrictedCat")
    session.add(category)
    session.commit()

    product = Product(sku="LOCK1", short_name="Product", category_id=category.id)
    session.add(product)
    session.commit()

    user = create_user_in_db(session, "User", "usr@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.put(f"/products/{product.id}", json={"is_active": False}, headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_update_product_with_existing_sku_fails(client, session):
    """Ensure update fails if SKU is already used by another product"""
    category = ProductCategory(name="DupCheck")
    session.add(category)
    session.commit()

    prod1 = Product(sku="ABC123", short_name="One", category_id=category.id)
    prod2 = Product(sku="DEF456", short_name="Two", category_id=category.id)
    session.add_all([prod1, prod2])
    session.commit()

    headers, _ = get_admin_headers(client, session)
    response = client.put(f"/products/{prod2.id}", json={"sku": "ABC123"}, headers=headers)
    assert response.status_code == 400
    assert "sku" in response.json()["detail"].lower()


def test_update_nonexistent_product_returns_404(client, session):
    """Ensure updating non-existent product returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.put("/products/9999", json={"short_name": "Ghost"}, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_admin_cannot_deactivate_product_with_stock(client, session): # this is new!!!
    category = ProductCategory(name="FakeCategory")
    session.add(category)
    session.commit()
    fake_prod = Product(sku="GHI123", short_name="FakeProd", category_id=category.id)
    session.add(fake_prod)
    session.commit()
    
    # Create warehouse required by FK
    session.add(Warehouse(id=555, description="WH555"))
    session.commit()

    # fake_prod has stock
    stock = Stock(product_id=fake_prod.id, warehouse_id=555, lot="NO_LOT", quantity=5)
    session.add(stock)
    session.commit()

    headers, _ = get_admin_headers(client, session)
    response = client.put(f"/products/{fake_prod.id}", json={"is_active": False}, headers=headers)

    session.refresh(fake_prod)
    assert response.status_code == 400
    assert fake_prod.is_active == True

def test_admin_can_deactivate_products_without_stock(client, session):
    category = ProductCategory(name="FakeCategory2")
    session.add(category)
    session.commit()
    fake_prod = Product(sku="GHI456", short_name="FakeProd2", category_id=category.id)
    session.add(fake_prod)
    session.commit()

    headers, _ = get_admin_headers(client, session)
    response = client.put(f"/products/{fake_prod.id}", json={"is_active": False}, headers=headers)

    session.refresh(fake_prod)
    assert response.status_code == 200
    assert fake_prod.is_active == False


# [X] PUT    /products/bulk-status

def test_admin_can_bulk_deactivate_products_without_stock(client, session):
    """Ensure admin can deactivate multiple products if they have no stock"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name="BulkCat")
    session.add(category)
    session.commit()

    p1 = Product(sku="BULK1", short_name="P1", category_id=category.id)
    p2 = Product(sku="BULK2", short_name="P2", category_id=category.id)
    session.add_all([p1, p2])
    session.commit()

    response = client.put(
        "/products/bulk-status",
        json={"ids": [p1.id, p2.id], "is_active": False},
        headers=headers,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "2 products updated"
    assert result["skipped"] == 0

    # Confirm in DB
    for pid in [p1.id, p2.id]:
        assert session.get(Product, pid).is_active is False


def test_admin_cannot_deactivate_product_with_stock(client, session):
    """Ensure product with stock cannot be deactivated"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name="StockCat")
    session.add(category)
    session.commit()

    p1 = Product(sku="STOCK1", short_name="HasStock", category_id=category.id)
    p2 = Product(sku="STOCK2", short_name="NoStock", category_id=category.id)
    session.add_all([p1, p2])
    session.commit()

    # Create warehouse required by FK
    session.add(Warehouse(id=1, description="WH1"))
    session.commit()

    # Only p1 has stock
    stock = Stock(product_id=p1.id, warehouse_id=1, lot="NO_LOT", quantity=5)
    session.add(stock)
    session.commit()

    response = client.put(
        "/products/bulk-status",
        json={"ids": [p1.id, p2.id], "is_active": False},
        headers=headers,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "1 products updated"
    assert result["skipped"] == 1

    assert session.get(Product, p1.id).is_active is True
    assert session.get(Product, p2.id).is_active is False


def test_regular_user_cannot_bulk_update_products(client, session):
    """Ensure non-admin users cannot update products in bulk"""
    user = create_user_in_db(session, "User", "user@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    category = ProductCategory(name="UserBlock")
    session.add(category)
    session.commit()

    product = Product(sku="LOCKP", short_name="Blocked", category_id=category.id)
    session.add(product)
    session.commit()

    response = client.put(
        "/products/bulk-status",
        json={"ids": [product.id], "is_active": False},
        headers=headers,
    )
    assert response.status_code == 403


# [X] DELETE /products/{id}
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse

def test_admin_can_delete_product_without_movements(client, session):
    """Ensure admin can delete a product with no stock movements"""
    headers, _ = get_admin_headers(client, session)
    category = ProductCategory(name="Deletable")
    session.add(category)
    session.commit()

    product = Product(sku="DEL001", short_name="ToDelete", category_id=category.id)
    session.add(product)
    session.commit()

    response = client.delete(f"/products/{product.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["sku"] == "DEL001"
    assert session.get(Product, product.id) is None


def test_admin_cannot_delete_product_with_movements(client, session):
    """Ensure admin cannot delete a product with stock movement lines"""
    headers, admin = get_admin_headers(client, session)

    # Prepare category, warehouse and product
    session.add(ProductCategory(id=1, name="Locked"))
    session.add(Warehouse(id=1, description="Main"))
    session.commit()

    product = Product(id=1, sku="LOCKDEL", short_name="Locked", category_id=1)
    session.add(product)
    session.commit()

    # Create movement + line
    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    line = StockMoveLine(
        move_id=move.move_id,
        line_id=1,
        product_id=1,
        warehouse_id=1,
        lot="NO_LOT",
        expiration_date=None,
        quantity=10
    )
    session.add(line)
    session.commit()

    response = client.delete("/products/1", headers=headers)
    assert response.status_code == 500
    assert "associated movements" in response.json()["detail"].lower()


def test_regular_user_cannot_delete_product(client, session):
    """Ensure non-admin users cannot delete products"""
    category = ProductCategory(name="Restricted")
    session.add(category)
    session.commit()

    product = Product(sku="USRDEL", short_name="Blocked", category_id=category.id)
    session.add(product)
    session.commit()

    user = create_user_in_db(session, "User", "user@x.com", "pass", is_active=True)
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    response = client.delete(f"/products/{product.id}", headers=headers)
    assert response.status_code == 403


def test_delete_nonexistent_product_returns_404(client, session):
    """Ensure deleting a non-existent product returns 404"""
    headers, _ = get_admin_headers(client, session)
    response = client.delete("/products/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
