"""
This test module covers all endpoints in the /stock-movements router.

TESTED ENDPOINTS:
[X] POST   /stock-movements/
[X] GET    /stock-movements/
[X] GET    /stock-movements/{move_id}
[X] GET    /stock-movements/{move_id}/lines
[X] GET    /stock-movements/summary/move-type
[X] GET    /stock-movements/last-year
"""

import pytest
from datetime import date, datetime, timedelta, timezone
from sqlmodel import select
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.product_category import ProductCategory
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.tests.utils import (
    create_user_in_db,
    get_admin_headers,
    get_auth_headers,
    get_token_for_user,
)


# [X] POST   /stock-movements/
def test_admin_can_create_movement_with_lines(client, session):
    """Ensure admin can create a stock movement with multiple lines"""
    # Create admin user and get headers
    headers, admin = get_admin_headers(client, session)

    # Setup: create category, warehouse and products
    category = ProductCategory(name="TestCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=1, description="Main Warehouse", is_active=True)
    session.add(warehouse)

    product1 = Product(
        id=1, sku="SKU1", short_name="Prod1", category_id=category.id, is_active=True
    )
    product2 = Product(
        id=2, sku="SKU2", short_name="Prod2", category_id=category.id, is_active=True
    )
    session.add_all([product1, product2])
    session.commit()

    # Define movement payload
    movement_payload = {
        "move_type": "incoming",
        "user_id": admin.id,
        "lines": [
            {
                "warehouse_id": warehouse.id,
                "product_id": product1.id,
                "lot": "LOT001",
                "expiration_date": None,
                "quantity": 5,
            },
            {
                "warehouse_id": warehouse.id,
                "product_id": product2.id,
                "lot": "LOT002",
                "expiration_date": None,
                "quantity": 10,
            },
        ],
    }

    # Perform request
    response = client.post("/stock-movements/", json=movement_payload, headers=headers)

    # Assertions
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["move_type"] == "incoming"
    assert data["user_id"] == admin.id
    assert data["user_name"] == admin.name
    assert len(data["lines"]) == 2
    assert data["lines"][0]["product_id"] == product1.id
    assert data["lines"][1]["product_id"] == product2.id


def test_user_can_create_own_movement(client, session):
    """Ensure regular user can create a movement for themselves"""
    # Create user and get headers
    user = create_user_in_db(
        session, "User", "user@example.com", "testpass", role="user", is_active=True
    )
    token = get_token_for_user(client, user.email, "testpass")
    headers = get_auth_headers(token)

    # Setup: category, warehouse, product
    category = ProductCategory(name="UserCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=10, description="User WH", is_active=True)
    session.add(warehouse)

    product = Product(
        id=10,
        sku="U001",
        short_name="UserProd",
        category_id=category.id,
        is_active=True,
    )
    session.add(product)
    session.commit()

    # Valid payload
    payload = {
        "move_type": "outgoing",
        "user_id": user.id,
        "lines": [
            {
                "warehouse_id": warehouse.id,
                "product_id": product.id,
                "lot": "LOT-USER",
                "expiration_date": None,
                "quantity": 3,
            }
        ],
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["move_type"] == "outgoing"
    assert data["user_id"] == user.id
    assert data["user_name"] == user.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["quantity"] == 3


def test_user_cannot_create_movement_for_another_user(client, session):
    """Ensure a regular user cannot create a movement for another user (forbidden)"""
    # Create two users
    user1 = create_user_in_db(
        session, "User1", "u1@example.com", "pass1", is_active=True
    )
    user2 = create_user_in_db(
        session, "User2", "u2@example.com", "pass2", is_active=True
    )

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    # Setup category, warehouse, product
    category = ProductCategory(name="Cross")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=20, description="WH", is_active=True)
    product = Product(
        id=20, sku="SKU-X", short_name="X", category_id=category.id, is_active=True
    )
    session.add_all([warehouse, product])
    session.commit()

    payload = {
        "move_type": "incoming",
        "user_id": user2.id,  # <- user1 tries to register for user2
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 2}
        ],
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)

    assert response.status_code == 403
    assert "another user" in response.json()["detail"].lower()


def test_movement_requires_at_least_one_line(client, session):
    """Ensure movement creation fails if no lines are provided"""
    headers, admin = get_admin_headers(client, session)

    payload = {
        "move_type": "incoming",
        "user_id": admin.id,
        "lines": [],  # <- Empty on purpose
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)

    assert response.status_code == 400
    assert "at least one line" in response.json()["detail"].lower()





def test_movement_rejects_expired_lot_in_incoming(client, session):
    """Ensure incoming movement with expired expiration date is rejected"""
    headers, admin = get_admin_headers(client, session)

    # Setup: category, active warehouse, active product
    category = ProductCategory(name="ExpCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=30, description="WH Exp", is_active=True)
    product = Product(
        id=30,
        sku="EXP123",
        short_name="Expired",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    expired_date = date.today() - timedelta(days=1)

    payload = {
        "move_type": "incoming",
        "user_id": admin.id,
        "lines": [
            {
                "warehouse_id": warehouse.id,
                "product_id": product.id,
                "expiration_date": str(expired_date),
                "quantity": 1,
            }
        ],
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_movement_rejects_inactive_warehouse(client, session):
    """Ensure movement creation fails if warehouse is inactive"""
    headers, admin = get_admin_headers(client, session)

    category = ProductCategory(name="InactiveWH")
    session.add(category)
    session.commit()

    # Inactive warehouse
    warehouse = Warehouse(id=40, description="Disabled WH", is_active=False)
    session.add(warehouse)

    # Inactive product
    product = Product(
        id=40, sku="WH001", short_name="WHProd", category_id=category.id, is_active=True
    )
    session.add(product)
    session.commit()

    payload = {
        "move_type": "incoming",
        "user_id": admin.id,
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 2}
        ],
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "warehouses are inactive" in response.json()["detail"].lower()


def test_movement_rejects_inactive_product(client, session):
    """Ensure movement creation fails if product is inactive"""
    headers, admin = get_admin_headers(client, session)

    category = ProductCategory(name="InactiveProd")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=50, description="WH50", is_active=True)
    session.add(warehouse)

    # Inactive product
    product = Product(
        id=50,
        sku="PRD50",
        short_name="Inactive",
        category_id=category.id,
        is_active=False,
    )
    session.add(product)
    session.commit()

    payload = {
        "move_type": "incoming",
        "user_id": admin.id,
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 5}
        ],
    }

    response = client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "products are inactive" in response.json()["detail"].lower()


def test_movement_rejects_more_than_100_lines(client, session):
    """Ensure movement creation fails if more than 100 lines are provided"""
    headers, admin = get_admin_headers(client, session)

    # Setup: category, warehouse and product (reused in all of the lines)
    category = ProductCategory(name="LimitCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=60, description="WH60", is_active=True)
    product = Product(
        id=60,
        sku="SKU60",
        short_name="LimitProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create 101 valid lines
    lines = [
        {
            "warehouse_id": warehouse.id,
            "product_id": product.id,
            "lot": f"LOTE{i}",
            "expiration_date": None,
            "quantity": 1,
        }
        for i in range(101)
    ]

    payload = {"move_type": "incoming", "user_id": admin.id, "lines": lines}

    response = client.post("/stock-movements/", json=payload, headers=headers)

    assert response.status_code == 400
    assert "maximum number of allowed lines" in response.json()["detail"].lower()


# [X] GET    /stock-movements/
def test_admin_can_list_all_movements(client, session):
    """Ensure admin can retrieve all stock movements"""
    headers, admin = get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="CatGET")
    session.add(category)
    session.commit()
    warehouse = Warehouse(id=70, description="WH70", is_active=True)
    product = Product(
        id=70,
        sku="SKU70",
        short_name="GETPROD",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([category, warehouse, product])
    session.commit()

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    line = StockMoveLine(
        move_id=move.move_id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=10,
    )
    session.add(line)
    session.commit()

    response = client.get("/stock-movements/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert isinstance(data["data"], list)
    assert any(m["move_id"] == move.move_id for m in data["data"])


def test_user_can_only_see_own_movements(client, session):
    """Ensure a regular user only sees their own movements"""
    # Create user1 and user2
    user1 = create_user_in_db(session, "User1", "u1@email.com", "pass1", is_active=True)
    user2 = create_user_in_db(session, "User2", "u2@email.com", "pass2", is_active=True)

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    # Common setup
    category = ProductCategory(name="Restrict")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=80, description="WH80", is_active=True)
    product = Product(
        id=80, sku="SKU80", short_name="Own", category_id=category.id, is_active=True
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create user1 stock movement
    move1 = StockMove(move_type="incoming", user_id=user1.id)
    session.add(move1)
    session.commit()
    session.refresh(move1)

    line1 = StockMoveLine(
        move_id=move1.move_id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=5,
    )
    session.add(line1)

    # Create user2 stock movement
    move2 = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move2)
    session.commit()
    session.refresh(move2)

    line2 = StockMoveLine(
        move_id=move2.move_id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=5,
    )
    session.add(line2)
    session.commit()

    # user1 should only see their own stock movement
    response = client.get("/stock-movements/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert all(m["user_id"] == user1.id for m in data["data"])


def test_admin_can_filter_movements_by_search(client, session):
    """Ensure admin can filter movements by user name (case-insensitive)"""
    headers, admin = get_admin_headers(client, session)

    # Create other user with searchable name
    user = create_user_in_db(
        session, "Paquito", "paquito@example.com", "pass", is_active=True
    )

    # Common setup
    category = ProductCategory(name="SearchCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=90, description="WH90", is_active=True)
    product = Product(
        id=90,
        sku="SKU90",
        short_name="ProdSearch",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create a new movement with that user
    move = StockMove(move_type="incoming", user_id=user.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    line = StockMoveLine(
        move_id=move.move_id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=1,
    )
    session.add(line)
    session.commit()

    # Search with partial name
    response = client.get("/stock-movements/?search=paqui", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("paquito" in m["user_name"].lower() for m in data["data"])


def test_admin_can_filter_movements_by_move_type(client, session):
    """Ensure admin can filter movements by move_type"""
    headers, admin = get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="MoveTypeCat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=100, description="WH100", is_active=True)
    product = Product(
        id=100,
        sku="SKU100",
        short_name="Prod100",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create different types of movement
    move_in = StockMove(move_type="incoming", user_id=admin.id)
    move_out = StockMove(move_type="outgoing", user_id=admin.id)
    session.add_all([move_in, move_out])
    session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_in.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_out.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    session.commit()

    # Filter by "incoming"
    response_in = client.get("/stock-movements/?move_type=incoming", headers=headers)
    assert response_in.status_code == 200
    assert all(m["move_type"] == "incoming" for m in response_in.json()["data"])

    # Filter by "outgoing"
    response_out = client.get("/stock-movements/?move_type=outgoing", headers=headers)
    assert response_out.status_code == 200
    assert all(m["move_type"] == "outgoing" for m in response_out.json()["data"])


def test_admin_can_filter_movements_by_date_range(client, session):
    """Ensure admin can filter movements using date_from and date_to"""
    headers, admin = get_admin_headers(client, session)

    # Setup: category, warehouse, product
    category = ProductCategory(name="Datecat")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=110, description="WH110", is_active=True)
    product = Product(
        id=110,
        sku="SKU110",
        short_name="DateProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create movements with different dates
    today = datetime.now(timezone.utc)
    one_week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    move_recent = StockMove(
        move_type="incoming", user_id=admin.id, created_at=one_week_ago
    )
    move_old = StockMove(
        move_type="incoming", user_id=admin.id, created_at=two_weeks_ago
    )
    session.add_all([move_recent, move_old])
    session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_recent.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_old.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    session.commit()

    # Filter: only movements after 10 days ago
    date_from = (today - timedelta(days=10)).date().isoformat()
    response = client.get(f"/stock-movements/?date_from={date_from}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert all(
        datetime.fromisoformat(m["created_at"]).date()
        >= datetime.fromisoformat(date_from).date()
        for m in data["data"]
    )


def test_admin_can_filter_movements_by_user_id(client, session):
    """Ensure admin can filter movements by specific user ID"""
    headers, admin = get_admin_headers(client, session)

    # Create a second user
    user = create_user_in_db(
        session, "TargetUser", "target@example.com", "pass", is_active=True
    )

    # Setup: Category, Warehouse, Product
    category = ProductCategory(name="Filtered")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=120, description="WH120", is_active=True)
    product = Product(
        id=120,
        sku="SKU120",
        short_name="UserProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create movements for both users
    move_admin = StockMove(move_type="incoming", user_id=admin.id)
    move_user = StockMove(move_type="incoming", user_id=user.id)
    session.add_all([move_admin, move_user])
    session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_admin.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_user.move_id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    session.commit()

    # Filter by user.id
    response = client.get(f"/stock-movements/?user_id={user.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert all(m["user_id"] == user.id for m in data["data"])


# [X] GET    /stock-movements/{move_id}


def test_admin_can_view_any_movement_details(client, session):
    """Ensure admin can retrieve the full details of any movement"""
    headers, admin = get_admin_headers(client, session)

    # Setup: Category, Warehouse, Product
    category = ProductCategory(name="Detail")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=130, description="WH130", is_active=True)
    product = Product(
        id=130,
        sku="SKU130",
        short_name="DetailProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create movement with lines
    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=5,
        )
    )
    session.commit()

    # Request detail
    response = client.get(f"/stock-movements/{move.move_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["move_id"] == move.move_id
    assert data["user_id"] == admin.id
    assert data["user_name"] == admin.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["product_id"] == product.id


def test_get_nonexistent_movement_returns_404(client, session):
    """Ensure request returns 404 when movement does not exist"""
    headers, _ = get_admin_headers(client, session)

    response = client.get("/stock-movements/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_user_cannot_view_other_user_movement(client, session):
    """Ensure a user cannot view movement belonging to another user"""
    # Create two users
    user1 = create_user_in_db(
        session, "UserOne", "u1@email.com", "pass1", is_active=True
    )
    user2 = create_user_in_db(
        session, "UserTwo", "u2@email.com", "pass2", is_active=True
    )

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    # Setup
    category = ProductCategory(name="Private")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=140, description="WH140", is_active=True)
    product = Product(
        id=140, sku="SKU140", short_name="Prod", category_id=category.id, is_active=True
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create movement for user2
    move = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=1,
        )
    )
    session.commit()

    # User1 tries to access user2’s movement
    response = client.get(f"/stock-movements/{move.move_id}", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_user_can_view_own_movement(client, session):
    """Ensure a user can view details of their own movement"""
    user = create_user_in_db(
        session, "RegularUser", "me@example.com", "pass", is_active=True
    )
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    # Setup
    category = ProductCategory(name="Personal")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=150, description="WH150", is_active=True)
    product = Product(
        id=150,
        sku="SKU150",
        short_name="MyProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    # Create movement for this user
    move = StockMove(move_type="outgoing", user_id=user.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=2,
        )
    )
    session.commit()

    # User requests own movement
    response = client.get(f"/stock-movements/{move.move_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["move_id"] == move.move_id
    assert data["user_id"] == user.id
    assert data["user_name"] == user.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["quantity"] == 2


# [X] GET    /stock-movements/{move_id}/lines


def test_admin_can_view_movement_lines_with_names(client, session):
    """Ensure admin can view lines of a movement with product and warehouse names"""
    headers, admin = get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="Named")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=160, description="WH160", is_active=True)
    product = Product(
        id=160,
        sku="SKU160",
        short_name="NamedProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=10,
        )
    )
    session.commit()

    response = client.get(f"/stock-movements/{move.move_id}/lines", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    line = data["data"][0]
    assert line["product_name"] == product.short_name
    assert line["warehouse_name"] == warehouse.description


def test_user_can_view_own_movement_lines(client, session):
    """Ensure a regular user can view lines of their own movement"""
    user = create_user_in_db(
        session, "LineUser", "line@example.com", "pass", is_active=True
    )
    token = get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    # Setup
    category = ProductCategory(name="Owner")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=170, description="WH170", is_active=True)
    product = Product(
        id=170,
        sku="SKU170",
        short_name="OwnProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    move = StockMove(move_type="outgoing", user_id=user.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=4,
        )
    )
    session.commit()

    response = client.get(f"/stock-movements/{move.move_id}/lines", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["product_name"] == product.short_name


def test_get_lines_of_nonexistent_movement_returns_404(client, session):
    """Ensure request returns 404 when movement does not exist"""
    headers, _ = get_admin_headers(client, session)

    response = client.get("/stock-movements/9999/lines", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_user_cannot_view_lines_of_other_user_movement(client, session):
    """Ensure a user cannot view lines of a movement that is not theirs"""
    user1 = create_user_in_db(session, "U1", "u1@example.com", "pass1", is_active=True)
    user2 = create_user_in_db(session, "U2", "u2@example.com", "pass2", is_active=True)

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    # Setup
    category = ProductCategory(name="Restricted")
    session.add(category)
    session.commit()

    warehouse = Warehouse(id=180, description="WH180", is_active=True)
    product = Product(
        id=180,
        sku="SKU180",
        short_name="SecretProd",
        category_id=category.id,
        is_active=True,
    )
    session.add_all([warehouse, product])
    session.commit()

    move = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move)
    session.commit()
    session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.move_id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=1,
        )
    )
    session.commit()

    response = client.get(f"/stock-movements/{move.move_id}/lines", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


# [X] GET    /stock-movements/summary/move-type


def test_admin_can_view_movement_type_summary(client, session):
    """Ensure admin gets total incoming and outgoing movements"""
    headers, admin = get_admin_headers(client, session)

    # Setup
    session.add_all(
        [
            StockMove(move_type="incoming", user_id=admin.id),
            StockMove(move_type="incoming", user_id=admin.id),
            StockMove(move_type="outgoing", user_id=admin.id),
        ]
    )
    session.commit()

    response = client.get("/stock-movements/summary/move-type", headers=headers)
    assert response.status_code == 200
    data = response.json()

    incoming = next((x for x in data if x["move_type"] == "incoming"), None)
    outgoing = next((x for x in data if x["move_type"] == "outgoing"), None)

    assert incoming["quantity"] == 2
    assert outgoing["quantity"] == 1


def test_user_sees_only_their_own_movement_summary(client, session):
    """Ensure user sees movement type summary for their own movements only"""
    user1 = create_user_in_db(
        session, "User1", "u1@example.com", "pass1", is_active=True
    )
    user2 = create_user_in_db(
        session, "User2", "u2@example.com", "pass2", is_active=True
    )

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    # User1: 1 incoming
    # User2: 2 outgoing
    session.add_all(
        [
            StockMove(move_type="incoming", user_id=user1.id),
            StockMove(move_type="outgoing", user_id=user2.id),
            StockMove(move_type="outgoing", user_id=user2.id),
        ]
    )
    session.commit()

    response = client.get("/stock-movements/summary/move-type", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert any(m["move_type"] == "incoming" and m["quantity"] == 1 for m in data)
    assert all(m["move_type"] != "outgoing" or m["quantity"] == 0 for m in data)


# [X] GET    /stock-movements/last-year

def test_admin_can_view_all_movements_from_last_year(client, session):
    """Ensure admin receives all movements from last 12 months"""
    headers, admin = get_admin_headers(client, session)

    # Movement 1: within the last year
    recent_date = datetime.now(timezone.utc) - timedelta(days=30)
    move_recent = StockMove(
        move_type="incoming", user_id=admin.id, created_at=recent_date
    )

    # Movement 2: older than one year
    old_date = datetime.now(timezone.utc) - timedelta(days=400)
    move_old = StockMove(move_type="incoming", user_id=admin.id, created_at=old_date)

    session.add_all([move_recent, move_old])
    session.commit()

    response = client.get("/stock-movements/last-year", headers=headers)
    assert response.status_code == 200
    data = response.json()

    move_ids = [m["move_id"] for m in data]
    assert move_recent.move_id in move_ids
    assert move_old.move_id not in move_ids


def test_user_only_sees_own_movements_from_last_year(client, session):
    """Ensure user sees only their own movements from last 12 months"""
    user1 = create_user_in_db(
        session, "User1", "u1@example.com", "pass1", is_active=True
    )
    user2 = create_user_in_db(
        session, "User2", "u2@example.com", "pass2", is_active=True
    )

    token = get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    recent = datetime.now(timezone.utc) - timedelta(days=10)

    move_user1 = StockMove(move_type="incoming", user_id=user1.id, created_at=recent)
    move_user2 = StockMove(move_type="incoming", user_id=user2.id, created_at=recent)
    session.add_all([move_user1, move_user2])
    session.commit()

    response = client.get("/stock-movements/last-year", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert all(m["user_id"] == user1.id for m in data)
    assert move_user1.move_id in [m["move_id"] for m in data]
    assert move_user2.move_id not in [m["move_id"] for m in data]
