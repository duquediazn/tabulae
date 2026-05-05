"""
This test module covers all endpoints in the /stock router.

TESTED ENDPOINTS:
[x] GET    /stock/
[x] GET    /stock/warehouse/{warehouse_id}
[x] GET    /stock/warehouse/{warehouse_id}/detail
[x] GET    /stock/warehouses/detail
[x] GET    /stock/product/{product_id}
[x] GET    /stock/product-categories
[x] GET    /stock/category/{category_id}/products
[x] GET    /stock/product/expiration
[x] GET    /stock/semaphore
[x] GET    /stock/warehouse/{warehouse_id}/product/{product_id}
[x] GET    /stock/available-lots
[x] GET    /stock/history
[x] GET    /stock/product/{product_id}/history
[x] GET    /stock/warehouse/{warehouse_id}/history
[x] GET    /stock/warehouse/{warehouse_id}/product/{product_id}/history
"""

import pytest
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from app.models.product import Product
from app.models.stock import Stock
from app.models.stock_move import StockMove
from app.models.stock_move_line import StockMoveLine
from app.models.warehouse import Warehouse
from app.models.product_category import ProductCategory
from app.tests.utils import get_admin_headers
from datetime import date, timedelta


# [x] GET    /stock/


@pytest.mark.asyncio
async def test_admin_can_list_all_stock(client, session):
    """Ensure admin can retrieve global stock"""
    headers, _ = await get_admin_headers(client, session)

    # Setup: category, warehouse, product, stock
    category = ProductCategory(name="GlobalCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="Central WH", is_active=True)
    session.add(warehouse)
    await session.commit()

    product = Product(
        sku="STOCK001", short_name="Global Product", category_id=category.id
    )
    session.add(product)
    await session.commit()

    stock = Stock(warehouse_id=warehouse.id, product_id=product.id, lot="LOTE1", quantity=5)
    session.add(stock)
    await session.commit()

    response = await client.get("/stock/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert len(data["data"]) >= 1
    assert any(item["sku"] == "STOCK001" for item in data["data"])


@pytest.mark.asyncio
async def test_stock_total_is_full_count_not_capped_by_limit(client, session):
    """Verify that 'total' in paginated stock response reflects the real record count, not the limit."""
    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="PagCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="PagWH", is_active=True)
    session.add(warehouse)
    await session.commit()

    product = Product(sku="PAGSKU", short_name="PagProd", category_id=category.id)
    session.add(product)
    await session.commit()

    for i in range(15):
        session.add(Stock(warehouse_id=warehouse.id, product_id=product.id, lot=f"LOT{i:02d}", quantity=1))
    await session.commit()

    response = await client.get("/stock/?limit=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["data"]) == 5


# [x] GET    /stock/warehouse/{warehouse_id}


@pytest.mark.asyncio
async def test_admin_can_list_stock_by_warehouse(client, session):
    """Ensure admin can retrieve stock for a specific warehouse"""
    headers, _ = await get_admin_headers(client, session)

    # Setup (if not already from previous test)
    category = ProductCategory(name="WHCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="WH2", is_active=True)
    session.add(warehouse)
    await session.commit()

    product = Product(sku="WHSKU", short_name="WH Prod", category_id=category.id)
    session.add(product)
    await session.commit()

    stock = Stock(warehouse_id=warehouse.id, product_id=product.id, lot="WHLOT", quantity=10)
    session.add(stock)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert len(data["data"]) >= 1
    assert all(item["warehouse_id"] == warehouse.id for item in data["data"])
    assert any(item["sku"] == "WHSKU" for item in data["data"])


@pytest.mark.asyncio
async def test_stock_by_warehouse_returns_empty_for_no_stock(client, session):
    """Ensure warehouse returns empty stock list if no stock is present"""
    headers, _ = await get_admin_headers(client, session)

    # Create a warehouse without stock
    warehouse = Warehouse(name="Empty WH", is_active=True)
    session.add(warehouse)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["data"] == []


# [x] GET    /stock/warehouse/{warehouse_id}/detail


@pytest.mark.asyncio
async def test_admin_can_get_warehouse_pie_chart_data(client, session):
    """Ensure admin gets pie chart data (stock by product in a warehouse)"""
    headers, _ = await get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="PieCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="Pie WH", is_active=True)
    session.add(warehouse)
    await session.commit()

    product1 = Product(sku="SKU4A", short_name="ProdA", category_id=category.id)
    session.add(product1)
    await session.commit()
    product2 = Product(sku="SKU4B", short_name="ProdB", category_id=category.id)
    session.add(product2)
    await session.commit()

    stock1 = Stock(warehouse_id=warehouse.id, product_id=product1.id, lot="L1", quantity=10)
    session.add(stock1)
    await session.commit()
    stock2 = Stock(warehouse_id=warehouse.id, product_id=product2.id, lot="L2", quantity=15)
    session.add(stock2)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}/detail", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    total = sum(item["total_quantity"] for item in data)
    assert total == 25
    assert any(item["product_name"] == "ProdA" for item in data)
    assert any(item["product_name"] == "ProdB" for item in data)


# [x] GET    /stock/warehouses/detail


@pytest.mark.asyncio
async def test_admin_can_get_stock_summary_by_warehouse(client, session):
    """Ensure admin gets total stock per warehouse (bar chart)"""
    headers, _ = await get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="BarCat")
    session.add(category)
    await session.commit()

    wh1 = Warehouse(name="WH A", is_active=True)
    wh2 = Warehouse(name="WH B", is_active=True)
    session.add_all([wh1, wh2])
    await session.commit()

    prod = Product(sku="SKU6", short_name="BarProd", category_id=category.id)
    session.add(prod)
    await session.commit()

    stock1 = Stock(warehouse_id=wh1.id, product_id=prod.id, lot="X1", quantity=20)
    stock2 = Stock(warehouse_id=wh2.id, product_id=prod.id, lot="X2", quantity=30)
    session.add_all([stock1, stock2])
    await session.commit()

    response = await client.get("/stock/warehouses/detail", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 2
    assert any(
        item["warehouse_name"] == "WH A" and item["total_quantity"] == 20
        for item in data
    )
    assert any(
        item["warehouse_name"] == "WH B" and item["total_quantity"] == 30
        for item in data
    )


# [x] GET    /stock/product/{product_id}


@pytest.mark.asyncio
async def test_admin_can_get_stock_by_product(client, session):
    """Ensure admin can get stock summary for a specific product across warehouses"""
    headers, _ = await get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="ProdCat")
    session.add(category)
    await session.commit()

    product = Product(sku="PROD7", short_name="MultiWH", category_id=category.id)
    session.add(product)
    await session.commit()

    wh1 = Warehouse(name="WH7", is_active=True)
    wh2 = Warehouse(name="WH8", is_active=True)
    session.add_all([wh1, wh2])
    await session.commit()

    stock1 = Stock(warehouse_id=wh1.id, product_id=product.id, lot="L1", quantity=5)
    stock2 = Stock(warehouse_id=wh2.id, product_id=product.id, lot="L2", quantity=15)
    session.add_all([stock1, stock2])
    await session.commit()

    response = await client.get(f"/stock/product/{product.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    total_qty = sum(item["total_quantity"] for item in data["data"])
    assert total_qty == 20
    assert all(item["product_id"] == product.id for item in data["data"])


# [x] GET    /stock/product-categories


@pytest.mark.asyncio
async def test_admin_can_get_stock_by_category(client, session):
    """Ensure admin gets total stock grouped by category"""
    headers, _ = await get_admin_headers(client, session)

    # Setup
    cat1 = ProductCategory(name="Category A")
    cat2 = ProductCategory(name="Category B")
    session.add_all([cat1, cat2])
    await session.commit()

    wh = Warehouse(name="WH9", is_active=True)
    session.add(wh)
    await session.commit()

    p1 = Product(sku="SKA", short_name="A", category_id=cat1.id)
    p2 = Product(sku="SKB", short_name="B", category_id=cat2.id)
    session.add_all([p1, p2])
    await session.commit()

    stock1 = Stock(warehouse_id=wh.id, product_id=p1.id, lot="L", quantity=12)
    stock2 = Stock(warehouse_id=wh.id, product_id=p2.id, lot="L", quantity=8)
    session.add_all([stock1, stock2])
    await session.commit()

    response = await client.get("/stock/product-categories", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert any(
        item["category_name"] == "Category A" and item["total_quantity"] == 12
        for item in data
    )
    assert any(
        item["category_name"] == "Category B" and item["total_quantity"] == 8
        for item in data
    )


# [x] GET    /stock/category/{category_id}/products


@pytest.mark.asyncio
async def test_admin_can_get_stock_by_category_detail(client, session):
    """Ensure admin gets stock per product inside a specific category"""
    headers, _ = await get_admin_headers(client, session)

    # Setup
    cat = ProductCategory(name="DetailCat")
    session.add(cat)
    await session.commit()

    wh = Warehouse(name="WH10", is_active=True)
    session.add(wh)
    await session.commit()

    prod1 = Product(sku="D1", short_name="P1", category_id=cat.id)
    prod2 = Product(sku="D2", short_name="P2", category_id=cat.id)
    session.add_all([prod1, prod2])
    await session.commit()

    s1 = Stock(warehouse_id=wh.id, product_id=prod1.id, lot="A", quantity=6)
    s2 = Stock(warehouse_id=wh.id, product_id=prod2.id, lot="B", quantity=4)
    session.add_all([s1, s2])
    await session.commit()

    response = await client.get(f"/stock/category/{cat.id}/products", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert any(
        item["product_name"] == "P1" and item["total_quantity"] == 6 for item in data
    )
    assert any(
        item["product_name"] == "P2" and item["total_quantity"] == 4 for item in data
    )


@pytest.mark.asyncio
async def test_category_with_no_stock_returns_empty_list(client, session):
    """Ensure category detail returns empty list if no stock exists"""
    headers, _ = await get_admin_headers(client, session)

    # Create category and product without stock
    category = ProductCategory(name="EmptyStockCat")
    session.add(category)
    await session.commit()

    product = Product(sku="EMPTYSKU", short_name="Empty", category_id=category.id)
    session.add(product)
    await session.commit()

    response = await client.get(f"/stock/category/{category.id}/products", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data == []


# [x] GET    /stock/product/expiration

@pytest.mark.asyncio
async def test_admin_can_get_expired_products(client, session):
    """Admin should retrieve products expired or expiring within 1 month."""

    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="CatExpired")
    session.add(category)
    await session.commit()

    product = Product(
        sku="EXPIRED01", short_name="Expired", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Expired", is_active=True)
    session.add(warehouse)
    await session.commit()

    today = date.today()
    in_10_days = today + timedelta(days=10)

    stock = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="LOT1",
        expiration_date=in_10_days,   # ≤ 1 mes → expired
        quantity=5,
    )
    session.add(stock)
    await session.commit()

    response = await client.get(
        "/stock/product/expiration?preset=expired",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["sku"] == "EXPIRED01"

@pytest.mark.asyncio
async def test_admin_can_get_expiring_soon_products(client, session):
    """Admin should retrieve products expiring between 1 and 6 months."""

    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="CatSoon")
    session.add(category)
    await session.commit()

    product = Product(
        sku="SOON01", short_name="Soon", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Soon", is_active=True)
    session.add(warehouse)
    await session.commit()

    today = date.today()
    in_2_months = today + relativedelta(months=2)

    stock = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="LOT2",
        expiration_date=in_2_months,
        quantity=7,
    )
    session.add(stock)
    await session.commit()

    response = await client.get(
        "/stock/product/expiration?preset=expiring_soon",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["sku"] == "SOON01"

@pytest.mark.asyncio
async def test_admin_can_get_no_expiration_products(client, session):
    """Admin should retrieve products with no expiration or >6 months."""

    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="CatNoExp")
    session.add(category)
    await session.commit()

    product = Product(
        sku="NOEXP01", short_name="NoExp", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH NoExp", is_active=True)
    session.add(warehouse)
    await session.commit()

    # stock without expiration
    stock = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="LOT3",
        expiration_date=None,
        quantity=10,
    )
    session.add(stock)
    await session.commit()

    response = await client.get(
        "/stock/product/expiration?preset=no_expiration",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["sku"] == "NOEXP01"

@pytest.mark.asyncio
async def test_admin_can_get_products_by_date_range(client, session):
    """Admin can retrieve products within a custom date range."""

    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="CatDateRange")
    session.add(category)
    await session.commit()

    product = Product(
        sku="RANGE01", short_name="Range", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Range", is_active=True)
    session.add(warehouse)
    await session.commit()

    today = date.today()
    in_45_days = today + timedelta(days=45)

    stock = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="LOT4",
        expiration_date=in_45_days,
        quantity=8,
    )
    session.add(stock)
    await session.commit()

    response = await client.get(
        f"/stock/product/expiration?from_date={today}&to_date={today + timedelta(days=60)}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["sku"] == "RANGE01"

@pytest.mark.asyncio
async def test_expiration_requires_filters(client, session):
    headers, _ = await get_admin_headers(client, session)

    response = await client.get("/stock/product/expiration", headers=headers)

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_cannot_mix_preset_and_dates(client, session):
    headers, _ = await get_admin_headers(client, session)

    today = date.today()

    response = await client.get(
        f"/stock/product/expiration?preset=expired&from_date={today}",
        headers=headers,
    )

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_invalid_date_range_returns_400(client, session):
    headers, _ = await get_admin_headers(client, session)

    today = date.today()
    tomorrow = today + timedelta(days=1)

    response = await client.get(
        f"/stock/product/expiration?from_date={tomorrow}&to_date={today}",
        headers=headers,
    )

    assert response.status_code == 400


# [x] GET    /stock/semaphore

@pytest.mark.asyncio
async def test_admin_can_get_semaphore_stock_summary(client, session):
    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="SemaforoCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="WH Sem", is_active=True)
    session.add(warehouse)
    await session.commit()

    product1 = Product(sku="NOW", short_name="Now", category_id=category.id)
    product2 = Product(sku="SOON", short_name="Soon", category_id=category.id)
    product3 = Product(sku="LATE", short_name="Late", category_id=category.id)

    session.add_all([product1, product2, product3])
    await session.commit()

    today = date.today()
    in_20_days = today + timedelta(days=20)    # expired
    in_2_months = today + timedelta(days=60)   # expiring_soon
    in_7_months = today + timedelta(days=210)  # no_expiration

    s1 = Stock(warehouse_id=warehouse.id, product_id=product1.id, lot="S1", expiration_date=in_20_days, quantity=3)
    s2 = Stock(warehouse_id=warehouse.id, product_id=product2.id, lot="S2", expiration_date=in_2_months, quantity=7)
    s3 = Stock(warehouse_id=warehouse.id, product_id=product3.id, lot="S3", expiration_date=in_7_months, quantity=10)

    session.add_all([s1, s2, s3])
    await session.commit()

    response = await client.get("/stock/semaphore", headers=headers)
    data = response.json()

    assert data["expired"] == 3
    assert data["expiring_soon"] == 7
    assert data["no_expiration"] == 10


# [x] GET    /stock/warehouse/{warehouse_id}/product/{product_id}


@pytest.mark.asyncio
async def test_admin_can_get_stock_by_product_and_warehouse(client, session):
    """Ensure admin can retrieve stock for a product in a specific warehouse"""
    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="MixedCat")
    session.add(category)
    await session.commit()

    product = Product(sku="MIX1", short_name="Combo", category_id=category.id)
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Combo", is_active=True)
    session.add(warehouse)
    await session.commit()

    stock = Stock(warehouse_id=warehouse.id, product_id=product.id, lot="LOTCOMBO", quantity=8)
    session.add(stock)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}/product/{product.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["data"][0]["sku"] == "MIX1"
    assert data["data"][0]["lot"] == "LOTCOMBO"


# [x] GET    /stock/available-lots


@pytest.mark.asyncio
async def test_admin_can_get_available_lots_for_product_and_warehouse(client, session):
    """Ensure admin can retrieve all available lots (quantity > 0) for a product in a warehouse"""
    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="LotTestCat")
    session.add(category)
    await session.commit()

    warehouse = Warehouse(name="WH Lots", is_active=True)
    session.add(warehouse)
    await session.commit()

    product = Product(sku="LOTSKU", short_name="Lotty", category_id=category.id)
    session.add(product)
    await session.commit()

    s1 = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="L1",
        expiration_date=date.today() + timedelta(days=30),
        quantity=4,
    )
    s2 = Stock(
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="L2",
        expiration_date=date.today() + timedelta(days=60),
        quantity=0,
    )  # Should be excluded
    s3 = Stock(
        warehouse_id=warehouse.id, product_id=product.id, lot="L3", expiration_date=None, quantity=2
    )
    session.add_all([s1, s2, s3])
    await session.commit()

    response = await client.get(
        f"/stock/available-lots?product={product.id}&warehouse={warehouse.id}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    lots = [lot["lot"] for lot in data]
    assert "L1" in lots
    assert "L3" in lots
    assert all(lot["quantity"] > 0 for lot in data)


@pytest.mark.asyncio
async def test_available_lots_returns_empty_when_no_quantity(client, session):
    """Ensure no lots are returned if all have zero quantity"""
    headers, _ = await get_admin_headers(client, session)

    category = ProductCategory(name="ZeroCat")
    session.add(category)
    await session.commit()

    product = Product(
        sku="ZEROSKU", short_name="ZeroStock", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Zero", is_active=True)
    session.add(warehouse)
    await session.commit()

    # All lots with quantity = 0
    s1 = Stock(warehouse_id=warehouse.id, product_id=product.id, lot="ZERO1", quantity=0)
    s2 = Stock(warehouse_id=warehouse.id, product_id=product.id, lot="ZERO2", quantity=0)
    session.add_all([s1, s2])
    await session.commit()

    response = await client.get(
        f"/stock/available-lots?product={product.id}&warehouse={warehouse.id}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data == []


# [x] GET    /stock/history


@pytest.mark.asyncio
async def test_admin_can_get_full_stock_history(client, session):
    """Ensure admin can retrieve the full stock movement history"""
    headers, admin = await get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="HistCat")
    session.add(category)
    await session.commit()

    product = Product(
        sku="HIST001", short_name="HistProd", category_id=category.id
    )
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH Hist", is_active=True)
    session.add(warehouse)
    await session.commit()

    # Create a stock movement
    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="HLOT",
        quantity=10,
    )
    session.add(line)
    await session.commit()

    response = await client.get("/stock/history", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert any(item["sku"] == "HIST001" for item in data["data"])
    assert all("move_id" in item for item in data["data"])


# [x] GET    /stock/product/{product_id}/history


@pytest.mark.asyncio
async def test_admin_can_get_stock_history_by_product(client, session):
    """Ensure admin can retrieve stock movement history for a specific product"""
    headers, admin = await get_admin_headers(client, session)

    # Setup
    category = ProductCategory(name="HistByProd")
    session.add(category)
    await session.commit()

    product = Product(sku="HPROD", short_name="HistP", category_id=category.id)
    session.add(product)
    await session.commit()

    warehouse = Warehouse(name="WH HistProd", is_active=True)
    session.add(warehouse)
    await session.commit()

    from app.models.stock_move import StockMove
    from app.models.stock_move_line import StockMoveLine

    move = StockMove(move_type="outgoing", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="PL1",
        quantity=4,
    )
    session.add(line)
    await session.commit()

    response = await client.get(f"/stock/product/{product.id}/history", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["data"][0]["product_id"] == product.id
    assert data["data"][0]["lot"] == "PL1"


# [x] GET    /stock/warehouse/{warehouse_id}/history


@pytest.mark.asyncio
async def test_admin_can_get_stock_history_by_warehouse(client, session):
    """Ensure admin can retrieve stock movement history for a specific warehouse"""
    headers, admin = await get_admin_headers(client, session)

    # Setup: category
    category = ProductCategory(name="HistWH")
    session.add(category)
    await session.commit()

    # Setup: product
    product = Product(sku="HPROD", short_name="HistP", category_id=category.id)
    session.add(product)
    await session.commit()

    # Setup: warehouse
    warehouse = Warehouse(name="WH HistProd", is_active=True)
    session.add(warehouse)
    await session.commit()

    # Setup: stock movement
    from app.models.stock_move import StockMove
    from app.models.stock_move_line import StockMoveLine

    move = StockMove(move_type="outgoing", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="PL1",
        quantity=4,
    )
    session.add(line)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}/history", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["data"][0]["warehouse_id"] == warehouse.id
    assert data["data"][0]["lot"] == "PL1"


# [x] GET    /stock/warehouse/{warehouse_id}/product/{product_id}/history


@pytest.mark.asyncio
async def test_admin_can_get_stock_history_by_product_and_warehouse(client, session):
    """Ensure admin can retrieve movement history for a product in a specific warehouse"""
    headers, admin = await get_admin_headers(client, session)

    # Setup: category
    category = ProductCategory(name="HistCombo")
    session.add(category)
    await session.commit()

    # Setup: product
    product = Product(
        sku="COMBOHIST", short_name="ComboHist", category_id=category.id
    )
    session.add(product)
    await session.commit()

    # Setup: warehouse
    warehouse = Warehouse(name="WH ComboHist", is_active=True)
    session.add(warehouse)
    await session.commit()

    # Setup: movement
    from app.models.stock_move import StockMove
    from app.models.stock_move_line import StockMoveLine

    move = StockMove(move_type="incoming", user_id=admin.id)
    session.add(move)
    await session.commit()
    await session.refresh(move)

    line = StockMoveLine(
        move_id=move.id,
        line_id=1,
        warehouse_id=warehouse.id,
        product_id=product.id,
        lot="LXYZ",
        quantity=6,
    )
    session.add(line)
    await session.commit()

    response = await client.get(f"/stock/warehouse/{warehouse.id}/product/{product.id}/history", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["data"][0]["product_id"] == product.id
    assert data["data"][0]["warehouse_id"] == warehouse.id
    assert data["data"][0]["lot"] == "LXYZ"
