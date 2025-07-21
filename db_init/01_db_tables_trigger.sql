-- CREATION OF THE TABLES 
-- USERS
-- PostgreSQL 17 treats "user" and "stock" as reserved keywords or internal type names.
-- Therefore, we enclose them in double quotes ("user", "stock") to use them as table identifiers.
CREATE TABLE "user" ( 
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL
); 

-- WAREHOUSES
CREATE TABLE warehouse (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- PRODUCT CATEGORIES
CREATE TABLE product_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- PRODUCTS
CREATE TABLE product (
    id SERIAL PRIMARY KEY, 
    sku VARCHAR(20) UNIQUE NOT NULL, 
    short_name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    category_id INTEGER NOT NULL, 
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    FOREIGN KEY (category_id) REFERENCES product_category(id)
);

-- STOCK MOVES
CREATE TABLE stock_move (
    move_id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    move_type VARCHAR(10) CHECK (move_type IN ('incoming', 'outgoing')),
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

-- STOCK MOVE LINES
CREATE TABLE stock_move_line (
    move_id INT NOT NULL, 
    line_id INT NOT NULL CHECK (line_id > 0),  
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    lot VARCHAR(50) DEFAULT 'NO_LOT',
    expiration_date DATE,
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (move_id, line_id),  
    FOREIGN KEY (move_id) REFERENCES stock_move(move_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- STOCK
CREATE TABLE "stock" (
    warehouse_id INT REFERENCES warehouse(id) ON DELETE RESTRICT,
    product_id INT REFERENCES product(id) ON DELETE RESTRICT,
    lot VARCHAR(50) DEFAULT 'NO_LOT',
    expiration_date DATE,
    quantity INT CHECK (quantity >= 0),
    PRIMARY KEY (warehouse_id, product_id, lot) 
);


-- CREATION OF THE FUNCTION update_stock()
CREATE OR REPLACE FUNCTION update_stock() RETURNS TRIGGER AS $$
DECLARE 
    move_type_value VARCHAR(10);
    move_user INT;
    processed_lot VARCHAR(50);
BEGIN
    -- Retrieve the move type and user who created the stock move
    SELECT move_type, user_id INTO move_type_value, move_user 
    FROM stock_move 
    WHERE move_id = NEW.move_id;

    -- If lot is not specified, assign 'NO_LOT'
    processed_lot := COALESCE(NEW.lot, 'NO_LOT'); -- Replace NULL with 'NO_LOT'

    -- If the lot is 'NO_LOT' but an expiration date is provided, raise exception
    IF processed_lot = 'NO_LOT' AND NEW.expiration_date IS NOT NULL THEN
        RAISE EXCEPTION 'Cannot assign an expiration date to a product with no lot';
    END IF;

    -- If the lot exists but with a different expiration date, raise exception
    IF processed_lot <> 'NO_LOT' AND (
        SELECT COUNT(*) FROM "stock" WHERE warehouse_id = NEW.warehouse_id 
                                    AND product_id = NEW.product_id
                                    AND lot = processed_lot
                                    AND expiration_date <> NEW.expiration_date) > 0 THEN
        RAISE EXCEPTION 'Lot % already exists with a different expiration date', processed_lot;
    END IF;

    -- If it's an incoming movement, increase stock quantity
    IF move_type_value = 'incoming' THEN
        INSERT INTO "stock" (warehouse_id, product_id, lot, expiration_date, quantity)
        VALUES (NEW.warehouse_id, NEW.product_id, processed_lot, NEW.expiration_date, NEW.quantity)
        ON CONFLICT (warehouse_id, product_id, lot)
        DO UPDATE SET quantity = "stock".quantity + NEW.quantity;

    -- If it's an outgoing movement, decrease stock quantity
    ELSIF move_type_value = 'outgoing' THEN

        -- Check if there is enough stock before subtracting
        IF (SELECT quantity FROM "stock" WHERE warehouse_id = NEW.warehouse_id 
                                        AND product_id = NEW.product_id
                                        AND lot = processed_lot) < NEW.quantity OR 
           (SELECT COUNT(*) FROM "stock" WHERE warehouse_id = NEW.warehouse_id 
                                        AND product_id = NEW.product_id
                                        AND lot = processed_lot) = 0 THEN
            RAISE EXCEPTION 'Insufficient stock for product % in warehouse % with lot %', 
                            NEW.product_id, NEW.warehouse_id, processed_lot;
        END IF;

        -- Subtract the quantity from stock
        UPDATE "stock"
        SET quantity = GREATEST(0, quantity - NEW.quantity)
        WHERE warehouse_id = NEW.warehouse_id 
          AND product_id = NEW.product_id
          AND lot = processed_lot;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- CREATION OF THE TRIGGER
CREATE TRIGGER trg_update_stock
AFTER INSERT ON stock_move_line
FOR EACH ROW
EXECUTE FUNCTION update_stock();
