"""
This test module covers all endpoints in the /stock-movements router.

TESTED ENDPOINTS:
[X] POST   /stock-movements/
[X] GET    /stock-movements/
[X] GET    /stock-movements/{id}
[X] GET    /stock-movements/{id}/lines
[X] GET    /stock-movements/summary/move-type
[X] GET    /stock-movements/last-year
"""

import pytest
from datetime import date, datetime, timedelta, timezone
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
@pytest.mark.asyncio
async def test_admin_can_create_movement_with_lines(client, session, base_data):
    """Ensure admin can create a stock movement with multiple lines"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product1 = base_data.warehouse, base_data.product
    product2 = Product(sku="SKU2", short_name="Prod2", category_id=base_data.category.id, is_active=True)
    session.add(product2)
    await session.commit()

    movement_payload = {
        "move_type": "incoming",
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
    response = await client.post("/stock-movements/", json=movement_payload, headers=headers)

    # Assertions
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["move_type"] == "incoming"
    assert data["user_id"] == admin.id
    assert data["user_name"] == admin.name
    assert len(data["lines"]) == 2
    assert data["lines"][0]["product_id"] == product1.id
    assert data["lines"][1]["product_id"] == product2.id


@pytest.mark.asyncio
async def test_user_can_create_movement(client, session, base_data):
    """Ensure regular user can create a movement for themselves"""
    user = await create_user_in_db(
        session, "User", "user@example.com", "testpass", role="user", is_active=True
    )
    token = await get_token_for_user(client, user.email, "testpass")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    payload = {
        "move_type": "outgoing",
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

    response = await client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["move_type"] == "outgoing"
    assert data["user_id"] == user.id
    assert data["user_name"] == user.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["quantity"] == 3


@pytest.mark.asyncio
async def test_movement_is_always_created_for_authenticated_user(client, session, base_data):
    """Ensure movement is always assigned to the authenticated user"""
    user1 = await create_user_in_db(session, "User1", "u1@example.com", "pass1", is_active=True)
    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    payload = {
        "move_type": "incoming",
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 2}
        ],
    }

    response = await client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["user_id"] == user1.id


@pytest.mark.asyncio
async def test_movement_requires_at_least_one_line(client, session):
    """Ensure movement creation fails if no lines are provided"""
    headers, admin = await get_admin_headers(client, session)

    payload = {
        "move_type": "incoming",
        "lines": [],  # <- Empty on purpose
    }

    response = await client.post("/stock-movements/", json=payload, headers=headers)

    assert response.status_code == 400
    assert "at least one line" in response.json()["detail"].lower()





@pytest.mark.asyncio
async def test_movement_rejects_expired_lot_in_incoming(client, session, base_data):
    """Ensure incoming movement with expired expiration date is rejected"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

    expired_date = date.today() - timedelta(days=1)

    payload = {
        "move_type": "incoming",
        "lines": [
            {
                "warehouse_id": warehouse.id,
                "product_id": product.id,
                "expiration_date": str(expired_date),
                "quantity": 1,
            }
        ],
    }

    response = await client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_movement_rejects_inactive_warehouse(client, session, base_data):
    """Ensure movement creation fails if warehouse is inactive"""
    headers, admin = await get_admin_headers(client, session)

    warehouse = Warehouse(name="Disabled WH", is_active=False)
    session.add(warehouse)
    await session.commit()

    product = base_data.product

    payload = {
        "move_type": "incoming",
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 2}
        ],
    }

    response = await client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "warehouses are inactive" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_movement_rejects_inactive_product(client, session, base_data):
    """Ensure movement creation fails if product is inactive"""
    headers, admin = await get_admin_headers(client, session)

    warehouse = base_data.warehouse
    product = Product(sku="PRD50", short_name="Inactive", category_id=base_data.category.id, is_active=False)
    session.add(product)
    await session.commit()

    payload = {
        "move_type": "incoming",
        "lines": [
            {"warehouse_id": warehouse.id, "product_id": product.id, "quantity": 5}
        ],
    }

    response = await client.post("/stock-movements/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "products are inactive" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_movement_rejects_more_than_100_lines(client, session, base_data):
    """Ensure movement creation fails if more than 100 lines are provided"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

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

    payload = {"move_type": "incoming", "lines": lines}

    response = await client.post("/stock-movements/", json=payload, headers=headers)

    assert response.status_code == 400
    assert "maximum number of allowed lines" in response.json()["detail"].lower()


# [X] GET    /stock-movements/
@pytest.mark.asyncio
async def test_admin_can_list_all_movements(client, session, base_data):
    """Ensure admin can retrieve all stock movements"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=10,
    )
    session.add(line)
    await session.commit()

    response = await client.get("/stock-movements/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert isinstance(data["data"], list)
    assert any(m["id"] == move.id for m in data["data"])


@pytest.mark.asyncio
async def test_user_can_only_see_own_movements(client, session, base_data):
    """Ensure a regular user only sees their own movements"""
    user1 = await create_user_in_db(session, "User1", "u1@email.com", "pass1", is_active=True)
    user2 = await create_user_in_db(session, "User2", "u2@email.com", "pass2", is_active=True)

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    # Create user1 stock movement
    move1 = StockMove(move_type="incoming", user_id=user1.id)
    session.add(move1)
    await session.commit()
    await session.refresh(move1)

    line1 = StockMoveLine(
        move_id=move1.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=5,
    )
    session.add(line1)

    # Create user2 stock movement
    move2 = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move2)
    await session.commit()
    await session.refresh(move2)

    line2 = StockMoveLine(
        move_id=move2.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=5,
    )
    session.add(line2)
    await session.commit()

    # user1 should only see their own stock movement
    response = await client.get("/stock-movements/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert all(m["user_id"] == user1.id for m in data["data"])


@pytest.mark.asyncio
async def test_admin_can_filter_movements_by_search(client, session, base_data):
    """Ensure admin can filter movements by user name (case-insensitive)"""
    headers, admin = await get_admin_headers(client, session)

    user = await create_user_in_db(
        session, "Paquito", "paquito@example.com", "pass", is_active=True
    )

    warehouse, product = base_data.warehouse, base_data.product

    # Create a new movement with that user
    move = StockMove(move_type="incoming", user_id=user.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        quantity=1,
    )
    session.add(line)
    await session.commit()

    # Search with partial name
    response = await client.get("/stock-movements/?search=paqui", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("paquito" in m["user_name"].lower() for m in data["data"])


@pytest.mark.asyncio
async def test_admin_can_filter_movements_by_move_type(client, session, base_data):
    """Ensure admin can filter movements by move_type"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

    # Create different types of movement
    move_in = StockMove(move_type="incoming", user_id=admin.id)
    move_out = StockMove(move_type="outgoing", user_id=admin.id)
    session.add_all([move_in, move_out])
    await session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_in.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_out.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    await session.commit()

    # Filter by "incoming"
    response_in = await client.get("/stock-movements/?move_type=incoming", headers=headers)
    assert response_in.status_code == 200
    assert all(m["move_type"] == "incoming" for m in response_in.json()["data"])

    # Filter by "outgoing"
    response_out = await client.get("/stock-movements/?move_type=outgoing", headers=headers)
    assert response_out.status_code == 200
    assert all(m["move_type"] == "outgoing" for m in response_out.json()["data"])


@pytest.mark.asyncio
async def test_admin_can_filter_movements_by_date_range(client, session, base_data):
    """Ensure admin can filter movements using date_from and date_to"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

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
    await session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_recent.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_old.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    await session.commit()

    # Filter: only movements after 10 days ago
    date_from = (today - timedelta(days=10)).date().isoformat()
    response = await client.get(f"/stock-movements/?date_from={date_from}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert all(
        datetime.fromisoformat(m["created_at"]).date()
        >= datetime.fromisoformat(date_from).date()
        for m in data["data"]
    )


@pytest.mark.asyncio
async def test_admin_can_filter_movements_by_user_id(client, session, base_data):
    """Ensure admin can filter movements by specific user ID"""
    headers, admin = await get_admin_headers(client, session)

    user = await create_user_in_db(
        session, "TargetUser", "target@example.com", "pass", is_active=True
    )

    warehouse, product = base_data.warehouse, base_data.product

    # Create movements for both users
    move_admin = StockMove(move_type="incoming", user_id=admin.id)
    move_user = StockMove(move_type="incoming", user_id=user.id)
    session.add_all([move_admin, move_user])
    await session.commit()

    session.add_all(
        [
            StockMoveLine(
                move_id=move_admin.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
            StockMoveLine(
                move_id=move_user.id,
                line_id=1,
                warehouse_id=warehouse.id,
                product_id=product.id,
                quantity=1,
            ),
        ]
    )
    await session.commit()

    # Filter by user.id
    response = await client.get(f"/stock-movements/?user_id={user.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert all(m["user_id"] == user.id for m in data["data"])


# [X] GET    /stock-movements/{id}


@pytest.mark.asyncio
async def test_admin_can_view_any_movement_details(client, session, base_data):
    """Ensure admin can retrieve the full details of any movement"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

    # Create movement with lines
    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=5,
        )
    )
    await session.commit()

    # Request detail
    response = await client.get(f"/stock-movements/{move.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == move.id
    assert data["user_id"] == admin.id
    assert data["user_name"] == admin.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["product_id"] == product.id


@pytest.mark.asyncio
async def test_get_nonexistent_movement_returns_404(client, session):
    """Ensure request returns 404 when movement does not exist"""
    headers, _ = await get_admin_headers(client, session)

    response = await client.get("/stock-movements/9999", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_cannot_view_other_user_movement(client, session, base_data):
    """Ensure a user cannot view movement belonging to another user"""
    user1 = await create_user_in_db(
        session, "UserOne", "u1@email.com", "pass1", is_active=True
    )
    user2 = await create_user_in_db(
        session, "UserTwo", "u2@email.com", "pass2", is_active=True
    )

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    # Create movement for user2
    move = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=1,
        )
    )
    await session.commit()

    # User1 tries to access user2's movement
    response = await client.get(f"/stock-movements/{move.id}", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_can_view_own_movement(client, session, base_data):
    """Ensure a user can view details of their own movement"""
    user = await create_user_in_db(
        session, "RegularUser", "me@example.com", "pass", is_active=True
    )
    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    # Create movement for this user
    move = StockMove(move_type="outgoing", user_id=user.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=2,
        )
    )
    await session.commit()

    # User requests own movement
    response = await client.get(f"/stock-movements/{move.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == move.id
    assert data["user_id"] == user.id
    assert data["user_name"] == user.name
    assert len(data["lines"]) == 1
    assert data["lines"][0]["quantity"] == 2


# [X] GET    /stock-movements/{id}/lines


@pytest.mark.asyncio
async def test_admin_can_view_movement_lines_with_names(client, session, base_data):
    """Ensure admin can view lines of a movement with product and warehouse names"""
    headers, admin = await get_admin_headers(client, session)

    warehouse, product = base_data.warehouse, base_data.product

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=10,
        )
    )
    await session.commit()

    response = await client.get(f"/stock-movements/{move.id}/lines", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    line = data["data"][0]
    assert line["product_name"] == product.short_name
    assert line["warehouse_name"] == warehouse.name


@pytest.mark.asyncio
async def test_user_can_view_own_movement_lines(client, session, base_data):
    """Ensure a regular user can view lines of their own movement"""
    user = await create_user_in_db(
        session, "LineUser", "line@example.com", "pass", is_active=True
    )
    token = await get_token_for_user(client, user.email, "pass")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    move = StockMove(move_type="outgoing", user_id=user.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=4,
        )
    )
    await session.commit()

    response = await client.get(f"/stock-movements/{move.id}/lines", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["product_name"] == product.short_name


@pytest.mark.asyncio
async def test_get_lines_of_nonexistent_movement_returns_404(client, session):
    """Ensure request returns 404 when movement does not exist"""
    headers, _ = await get_admin_headers(client, session)

    response = await client.get("/stock-movements/9999/lines", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_user_cannot_view_lines_of_other_user_movement(client, session, base_data):
    """Ensure a user cannot view lines of a movement that is not theirs"""
    user1 = await create_user_in_db(session, "U1", "u1@example.com", "pass1", is_active=True)
    user2 = await create_user_in_db(session, "U2", "u2@example.com", "pass2", is_active=True)

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    warehouse, product = base_data.warehouse, base_data.product

    move = StockMove(move_type="incoming", user_id=user2.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    session.add(
        StockMoveLine(
            move_id=move.id,
            line_id=1,
            warehouse_id=warehouse.id,
            product_id=product.id,
            quantity=1,
        )
    )
    await session.commit()

    response = await client.get(f"/stock-movements/{move.id}/lines", headers=headers)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


# [X] GET    /stock-movements/summary/move-type


@pytest.mark.asyncio
async def test_admin_can_view_movement_type_summary(client, session):
    """Ensure admin gets total incoming and outgoing movements"""
    headers, admin = await get_admin_headers(client, session)

    # Setup
    session.add_all(
        [
            StockMove(move_type="incoming", user_id=admin.id),
            StockMove(move_type="incoming", user_id=admin.id),
            StockMove(move_type="outgoing", user_id=admin.id),
        ]
    )
    await session.commit()

    response = await client.get("/stock-movements/summary/move-type", headers=headers)
    assert response.status_code == 200
    data = response.json()

    incoming = next((x for x in data if x["move_type"] == "incoming"), None)
    outgoing = next((x for x in data if x["move_type"] == "outgoing"), None)

    assert incoming["quantity"] == 2
    assert outgoing["quantity"] == 1


@pytest.mark.asyncio
async def test_user_sees_only_their_own_movement_summary(client, session):
    """Ensure user sees movement type summary for their own movements only"""
    user1 = await create_user_in_db(
        session, "User1", "u1@example.com", "pass1", is_active=True
    )
    user2 = await create_user_in_db(
        session, "User2", "u2@example.com", "pass2", is_active=True
    )

    token = await get_token_for_user(client, user1.email, "pass1")
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
    await session.commit()

    response = await client.get("/stock-movements/summary/move-type", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert any(m["move_type"] == "incoming" and m["quantity"] == 1 for m in data)
    assert all(m["move_type"] != "outgoing" or m["quantity"] == 0 for m in data)


# [X] GET    /stock-movements/last-year

@pytest.mark.asyncio
async def test_admin_can_view_all_aggregated_movements_from_last_year(client, session):
    """Ensure admin receives aggregated data for all users in the last 12 months, excluding older movements."""
    headers, admin = await get_admin_headers(client, session)

    other_user = await create_user_in_db(
        session, "Other User", "other@example.com", "pass1234", is_active=True
    )

    recent_date = datetime.now(timezone.utc) - timedelta(days=30)
    # admin: 1 incoming; other_user: 1 outgoing — same month
    move_admin = StockMove(move_type="incoming", user_id=admin.id, created_at=recent_date)
    move_other = StockMove(move_type="outgoing", user_id=other_user.id, created_at=recent_date)

    # Movement older than one year (should not appear in results)
    old_date = datetime.now(timezone.utc) - timedelta(days=400)
    move_old = StockMove(move_type="incoming", user_id=admin.id, created_at=old_date)

    session.add_all([move_admin, move_other, move_old])
    await session.commit()

    response = await client.get("/stock-movements/last-year", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Response is a list of monthly aggregates: {month, incoming, outgoing}
    assert isinstance(data, list)
    for entry in data:
        assert "month" in entry
        assert "incoming" in entry
        assert "outgoing" in entry

    # Admin sees both users: at least 1 incoming (admin) and 1 outgoing (other_user)
    total_incoming = sum(entry["incoming"] for entry in data)
    total_outgoing = sum(entry["outgoing"] for entry in data)
    assert total_incoming >= 1
    assert total_outgoing >= 1

    # The old movement must not appear in the results
    months = [entry["month"] for entry in data]
    old_month = old_date.strftime("%Y-%m")
    assert not any(m.startswith(old_month) for m in months)


@pytest.mark.asyncio
async def test_user_only_sees_own_aggregated_movements_from_last_year(client, session):
    """Ensure user receives only their own movements aggregated, not other users'."""
    user1 = await create_user_in_db(
        session, "User1", "u1@example.com", "pass1", is_active=True
    )
    user2 = await create_user_in_db(
        session, "User2", "u2@example.com", "pass2", is_active=True
    )

    token = await get_token_for_user(client, user1.email, "pass1")
    headers = get_auth_headers(token)

    recent = datetime.now(timezone.utc) - timedelta(days=10)

    # user1: 1 incoming; user2: 1 outgoing — same month
    move_user1 = StockMove(move_type="incoming", user_id=user1.id, created_at=recent)
    move_user2 = StockMove(move_type="outgoing", user_id=user2.id, created_at=recent)
    session.add_all([move_user1, move_user2])
    await session.commit()

    response = await client.get("/stock-movements/last-year", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # user1 has 1 incoming and 0 outgoing; user2's outgoing must not appear
    total_incoming = sum(entry["incoming"] for entry in data)
    total_outgoing = sum(entry["outgoing"] for entry in data)
    assert total_incoming >= 1
    assert total_outgoing == 0
