-- 1. Delete dependent data
DELETE FROM stock_move_line;

DELETE FROM stock_move;

DELETE FROM "stock";

-- 2. Restart ID sequences for stock_move and others
ALTER SEQUENCE public.stock_move_move_id_seq
RESTART WITH 1;

ALTER SEQUENCE public.user_id_seq
RESTART WITH 1;

ALTER SEQUENCE public.warehouse_id_seq
RESTART WITH 1;

ALTER SEQUENCE public.product_category_id_seq
RESTART WITH 1;

ALTER SEQUENCE public.product_id_seq
RESTART WITH 1;

-- 3. Insert into stock_move
INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (1, CURRENT_DATE - INTERVAL '130 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (2, CURRENT_DATE - INTERVAL '129 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (3, CURRENT_DATE - INTERVAL '125 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (4, CURRENT_DATE - INTERVAL '125 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (5, CURRENT_DATE - INTERVAL '125 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (6, CURRENT_DATE - INTERVAL '124 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (7, CURRENT_DATE - INTERVAL '122 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (8, CURRENT_DATE - INTERVAL '122 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (9, CURRENT_DATE - INTERVAL '117 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (10, CURRENT_DATE - INTERVAL '112 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (11, CURRENT_DATE - INTERVAL '112 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (12, CURRENT_DATE - INTERVAL '112 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (13, CURRENT_DATE - INTERVAL '112 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (14, CURRENT_DATE - INTERVAL '111 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (15, CURRENT_DATE - INTERVAL '109 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (16, CURRENT_DATE - INTERVAL '109 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (17, CURRENT_DATE - INTERVAL '109 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (18, CURRENT_DATE - INTERVAL '105 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (19, CURRENT_DATE - INTERVAL '104 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (20, CURRENT_DATE - INTERVAL '102 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (21, CURRENT_DATE - INTERVAL '102 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (22, CURRENT_DATE - INTERVAL '102 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (23, CURRENT_DATE - INTERVAL '102 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (24, CURRENT_DATE - INTERVAL '98 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (25, CURRENT_DATE - INTERVAL '96 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (26, CURRENT_DATE - INTERVAL '96 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (27, CURRENT_DATE - INTERVAL '96 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (28, CURRENT_DATE - INTERVAL '96 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (29, CURRENT_DATE - INTERVAL '93 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (30, CURRENT_DATE - INTERVAL '90 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (31, CURRENT_DATE - INTERVAL '87 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (32, CURRENT_DATE - INTERVAL '87 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (33, CURRENT_DATE - INTERVAL '87 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (34, CURRENT_DATE - INTERVAL '84 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (35, CURRENT_DATE - INTERVAL '83 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (36, CURRENT_DATE - INTERVAL '75 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (37, CURRENT_DATE - INTERVAL '70 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (38, CURRENT_DATE - INTERVAL '70 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (39, CURRENT_DATE - INTERVAL '68 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (40, CURRENT_DATE - INTERVAL '68 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (41, CURRENT_DATE - INTERVAL '62 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (42, CURRENT_DATE - INTERVAL '62 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (43, CURRENT_DATE - INTERVAL '59 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (44, CURRENT_DATE - INTERVAL '56 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (45, CURRENT_DATE - INTERVAL '54 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (46, CURRENT_DATE - INTERVAL '53 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (47, CURRENT_DATE - INTERVAL '53 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (48, CURRENT_DATE - INTERVAL '53 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (49, CURRENT_DATE - INTERVAL '52 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (50, CURRENT_DATE - INTERVAL '52 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (51, CURRENT_DATE - INTERVAL '52 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (52, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (53, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (54, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (55, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (56, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (57, CURRENT_DATE - INTERVAL '49 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (58, CURRENT_DATE - INTERVAL '48 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (59, CURRENT_DATE - INTERVAL '48 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (60, CURRENT_DATE - INTERVAL '48 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (61, CURRENT_DATE - INTERVAL '48 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (62, CURRENT_DATE - INTERVAL '45 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (63, CURRENT_DATE - INTERVAL '45 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (64, CURRENT_DATE - INTERVAL '45 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (65, CURRENT_DATE - INTERVAL '45 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (66, CURRENT_DATE - INTERVAL '44 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (67, CURRENT_DATE - INTERVAL '44 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (68, CURRENT_DATE - INTERVAL '44 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (69, CURRENT_DATE - INTERVAL '42 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (70, CURRENT_DATE - INTERVAL '40 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (71, CURRENT_DATE - INTERVAL '37 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (72, CURRENT_DATE - INTERVAL '35 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (73, CURRENT_DATE - INTERVAL '33 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (74, CURRENT_DATE - INTERVAL '33 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (75, CURRENT_DATE - INTERVAL '31 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (76, CURRENT_DATE - INTERVAL '31 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (77, CURRENT_DATE - INTERVAL '31 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (78, CURRENT_DATE - INTERVAL '28 days', 'incoming', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (79, CURRENT_DATE - INTERVAL '28 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (80, CURRENT_DATE - INTERVAL '27 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (81, CURRENT_DATE - INTERVAL '26 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (82, CURRENT_DATE - INTERVAL '26 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (83, CURRENT_DATE - INTERVAL '26 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (84, CURRENT_DATE - INTERVAL '23 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (85, CURRENT_DATE - INTERVAL '21 days', 'incoming', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (86, CURRENT_DATE - INTERVAL '21 days', 'outgoing', 1);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (87, CURRENT_DATE - INTERVAL '21 days', 'incoming', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (88, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (89, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (90, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (91, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (92, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (93, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (94, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 3);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (95, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 2);

INSERT INTO
    stock_move (move_id, created_at, move_type, user_id)
VALUES
    (96, CURRENT_DATE - INTERVAL '19 days', 'outgoing', 3);

-- 4. Insert into stock_move_line
INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 1, 1, 1, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 2, 1, 2, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 3, 1, 3, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 4, 1, 4, 'NO_LOT', null, 50);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 5, 1, 5, 'NO_LOT', null, 12);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 6, 1, 6, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 7, 1, 7, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 8, 1, 8, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 9, 1, 9, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 10, 1, 10, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 11, 1, 11, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 12, 1, 12, 'NO_LOT', null, 12);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 13, 1, 13, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 14, 1, 14, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 15, 1, 15, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 16, 1, 16, 'OASIGFHA-123-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 17, 1, 16, 'OASIGFHA-122-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 18, 1, 16, 'OASIGFHA-121-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 19, 1, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 20, 1, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 21, 1, 19, 'L2024-12', CURRENT_DATE + INTERVAL '256 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 22, 1, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 23, 1, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 24, 1, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 60);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 25, 1, 27, 'OP_201235', CURRENT_DATE + INTERVAL '21 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (1, 26, 1, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (2, 1, 1, 18, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (2, 2, 1, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (2, 3, 1, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (2, 4, 1, 20, 'PK2024_1021', CURRENT_DATE + INTERVAL '156 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (3, 1, 1, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (3, 2, 1, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (3, 3, 1, 25, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (3, 4, 1, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 1, 1, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 2, 1, 12, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 3, 1, 13, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 4, 1, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 5, 1, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (4, 6, 1, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 2, 3, 12, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 3, 3, 13, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 4, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 5, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (5, 6, 3, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (6, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (6, 2, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (6, 3, 3, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (7, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (7, 2, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (7, 3, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (8, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (8, 2, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (8, 3, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (9, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (9, 2, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (9, 3, 3, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 1, 1, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 2, 1, 23, 'L_AHP23', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 3, 1, 26, 'SL_ASRAF23', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 4, 1, 16, 'OASIGFHA-124-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 5, 1, 16, 'OASIGFHA-125-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 6, 1, 16, 'OASIGFHA-126-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (10, 7, 1, 16, 'OASIGFHA-123-1PK', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 1, 1, 1, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 2, 1, 2, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 3, 1, 8, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 4, 1, 4, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 5, 1, 3, 'NO_LOT', null, 16);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 6, 1, 5, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 7, 1, 6, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 8, 1, 7, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 9, 1, 11, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 10, 1, 12, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 11, 1, 10, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 12, 1, 13, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 13, 1, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (11, 14, 1, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 1, 3, 1, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 2, 3, 2, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 3, 3, 8, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 4, 3, 4, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 5, 3, 3, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 6, 3, 5, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 7, 3, 6, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 8, 3, 7, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (12, 9, 3, 11, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 1, 2, 1, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 2, 2, 2, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 3, 2, 8, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 4, 2, 4, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 5, 2, 3, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 6, 2, 5, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 7, 2, 6, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 8, 2, 7, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 9, 2, 11, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 10, 2, 12, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 11, 2, 10, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 12, 2, 13, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 13, 2, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (13, 14, 2, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (14, 1, 2, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (14, 2, 2, 10, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (15, 1, 3, 8, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (16, 1, 3, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (16, 2, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (16, 3, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (17, 1, 2, 2, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (17, 2, 2, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (18, 1, 1, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (18, 2, 1, 21, 'MAR10_MC_2412_7', CURRENT_DATE + INTERVAL '64 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (18, 3, 1, 18, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (19, 1, 3, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (19, 2, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (20, 1, 3, 17, '202501', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (20, 2, 3, 2, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (20, 3, 3, 8, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (21, 1, 2, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (21, 2, 2, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (21, 3, 2, 11, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (22, 1, 2, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (23, 1, 2, 8, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (23, 2, 2, 29, 'XUXE1564_L2', CURRENT_DATE + INTERVAL '20 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (24, 1, 1, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (24, 2, 1, 20, 'PK2024_1243', CURRENT_DATE + INTERVAL '187 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 1, 1, 15, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 2, 1, 16, 'OASIGFHA-123-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 3, 1, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 4, 1, 18, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 5, 1, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 6, 1, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 7, 1, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 8, 1, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 9, 1, 14, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 10, 1, 9, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 11, 1, 20, 'PK2024_1021', CURRENT_DATE + INTERVAL '156 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 12, 1, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 13, 1, 26, 'SL_ASRAF23', null, 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 14, 1, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 15, 1, 16, 'OASIGFHA-123-1PK', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (25, 16, 1, 16, 'OASIGFHA-126-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 1, 3, 15, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 2, 3, 16, 'OASIGFHA-123-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 3, 3, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 4, 3, 18, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 5, 3, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 6, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 7, 3, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (26, 8, 3, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 1, 2, 15, 'NO_LOT', null, 15);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 2, 2, 14, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 3, 2, 9, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 4, 2, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 5, 2, 20, 'PK2024_1021', CURRENT_DATE + INTERVAL '156 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 6, 2, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 7, 2, 26, 'SL_ASRAF23', null, 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 8, 2, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 9, 2, 16, 'OASIGFHA-123-1PK', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 10, 2, 16, 'OASIGFHA-126-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (27, 11, 2, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (28, 1, 2, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (29, 1, 3, 7, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (29, 2, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (30, 1, 3, 8, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (31, 1, 3, 11, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (31, 2, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (31, 3, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (32, 1, 2, 2, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (32, 2, 2, 26, 'SL_ASRAF23', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (33, 1, 3, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (33, 2, 3, 21, 'MAR10_MC_2411_1', CURRENT_DATE + INTERVAL '19 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (33, 3, 3, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (33, 4, 3, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (34, 1, 1, 18, 'NO_LOT', null, 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (34, 2, 1, 23, 'L_AHP23', null, 7);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (35, 1, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (35, 2, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (36, 1, 3, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 1, 3, 10, 'NO_LOT', null, 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 2, 3, 9, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 3, 3, 14, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 4, 3, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 5, 3, 23, 'L_AHP23', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 6, 3, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (37, 7, 3, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 1, 1, 10, 'NO_LOT', null, 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 2, 1, 9, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 3, 1, 14, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 4, 1, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 5, 1, 23, 'L_AHP23', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 6, 1, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (38, 7, 1, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 1, 1, 16, 'OASIGFHA-122-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 2, 1, 16, 'OASIGFHA-121-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 3, 1, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 4, 1, 25, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 5, 1, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (39, 6, 1, 21, 'MAR10_MC_2412_7', CURRENT_DATE + INTERVAL '64 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 1, 2, 16, 'OASIGFHA-122-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 2, 2, 16, 'OASIGFHA-121-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 3, 2, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 4, 2, 25, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 5, 2, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (40, 6, 2, 21, 'MAR10_MC_2412_7', CURRENT_DATE + INTERVAL '64 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (41, 1, 2, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (41, 2, 2, 14, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (42, 1, 2, 16, 'OASIGFHA-121-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (43, 1, 3, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (43, 2, 3, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (43, 3, 3, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (44, 1, 1, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (44, 2, 1, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (44, 3, 1, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (45, 1, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (46, 1, 2, 2, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (46, 2, 2, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (47, 1, 2, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (48, 1, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (48, 2, 3, 30, 'HPXMAS24', CURRENT_DATE + INTERVAL '19 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (49, 1, 3, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (50, 1, 3, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (51, 1, 2, 7, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (51, 2, 2, 13, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (52, 1, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (53, 1, 2, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (54, 1, 2, 5, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (54, 2, 2, 21, 'MAR10_MC_2412_7', CURRENT_DATE + INTERVAL '64 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (55, 1, 3, 6, 'NO_LOT', null, 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (55, 2, 3, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (56, 1, 3, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (56, 2, 3, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (56, 3, 3, 14, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (57, 1, 3, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 1, 1, 18, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 2, 1, 3, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 3, 1, 16, 'OASIGFHA-124-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 4, 1, 16, 'OASIGFHA-125-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 5, 1, 25, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (58, 6, 1, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (59, 1, 2, 18, 'NO_LOT', null, 8);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (59, 2, 2, 3, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (59, 3, 2, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (60, 1, 3, 3, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (60, 2, 3, 16, 'OASIGFHA-124-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (60, 3, 3, 16, 'OASIGFHA-125-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (60, 4, 3, 25, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (60, 5, 3, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (61, 1, 2, 5, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (61, 2, 2, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (62, 1, 2, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (62, 2, 2, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (63, 1, 3, 16, 'OASIGFHA-123-1SR', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (63, 2, 3, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (64, 1, 2, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (65, 1, 3, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (65, 2, 3, 14, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (66, 1, 3, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (67, 1, 3, 8, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (67, 2, 3, 2, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (68, 1, 2, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (68, 2, 2, 17, '202502', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (68, 3, 2, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 1, 1, 5, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 2, 1, 6, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 3, 1, 17, '202503', CURRENT_DATE - INTERVAL '41 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 4, 1, 10, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 5, 1, 14, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 6, 1, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (69, 7, 1, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (70, 1, 2, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (70, 2, 2, 14, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (71, 1, 3, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (72, 1, 3, 24, 'PIK2306', CURRENT_DATE - INTERVAL '72 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (72, 2, 3, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (73, 1, 2, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (74, 1, 3, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (74, 2, 3, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 1, 1, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 2, 1, 14, 'NO_LOT', null, 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 3, 1, 5, 'NO_LOT', null, 7);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 4, 1, 17, '202503', CURRENT_DATE - INTERVAL '41 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 5, 1, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 6, 1, 6, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (75, 7, 1, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 1, 2, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 2, 2, 14, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 3, 2, 5, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 4, 2, 17, '202503', CURRENT_DATE - INTERVAL '41 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 5, 2, 6, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (76, 6, 2, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 1, 3, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 2, 3, 14, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 3, 3, 5, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 4, 3, 17, '202503', CURRENT_DATE - INTERVAL '41 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 5, 3, 22, 'COTUFA11', CURRENT_DATE - INTERVAL '12 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 6, 3, 6, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (77, 7, 3, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 1, 1, 22, 'COTUFA51', CURRENT_DATE + INTERVAL '506 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 2, 1, 21, 'MAR10_MC_2412_7', CURRENT_DATE + INTERVAL '64 days', 10);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 3, 1, 28, 'Z2025-04', CURRENT_DATE - INTERVAL '11 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 4, 1, 17, '202504', CURRENT_DATE - INTERVAL '11 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 5, 1, 25, 'NO_LOT', null, 50);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (78, 6, 1, 18, 'NO_LOT', null, 30);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (79, 1, 3, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (80, 1, 3, 5, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (80, 2, 3, 15, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (81, 1, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (81, 2, 3, 9, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (81, 3, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (82, 1, 2, 1, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (82, 2, 2, 14, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (82, 3, 2, 7, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (82, 4, 2, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (83, 1, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (84, 1, 3, 4, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (84, 2, 3, 11, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (85, 1, 2, 9, 'NO_LOT', null, 4);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (85, 2, 2, 25, 'NO_LOT', null, 40);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (85, 3, 2, 28, 'Z2025-04', CURRENT_DATE - INTERVAL '11 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (86, 1, 1, 27, 'OP_201235', CURRENT_DATE + INTERVAL '21 days', 13);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (86, 2, 1, 9, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (86, 3, 1, 25, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (86, 4, 1, 28, 'Z2025-04', CURRENT_DATE - INTERVAL '11 days', 6);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (87, 1, 3, 27, 'OP_201235', CURRENT_DATE + INTERVAL '21 days', 13);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (87, 2, 3, 9, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (87, 3, 3, 25, 'NO_LOT', null, 20);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (87, 4, 3, 28, 'Z2025-04', CURRENT_DATE - INTERVAL '11 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (88, 1, 2, 18, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (88, 2, 2, 25, 'NO_LOT', null, 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (89, 1, 2, 21, 'MAR10_MC_2411_2', CURRENT_DATE + INTERVAL '34 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (90, 1, 3, 29, 'XUXE1764_L2', CURRENT_DATE + INTERVAL '126 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (91, 1, 3, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (91, 2, 3, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (92, 1, 3, 18, 'NO_LOT', null, 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (93, 1, 3, 3, 'NO_LOT', null, 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (94, 1, 2, 27, 'OP_201234', CURRENT_DATE + INTERVAL '20 days', 5);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (94, 2, 2, 24, 'PIK2310', CURRENT_DATE + INTERVAL '50 days', 2);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (95, 1, 3, 19, 'L2024-07', CURRENT_DATE + INTERVAL '95 days', 3);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (96, 1, 2, 28, 'Z2025-01', CURRENT_DATE - INTERVAL '100 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (96, 2, 2, 28, 'Z2025-02', CURRENT_DATE - INTERVAL '72 days', 1);

INSERT INTO
    stock_move_line (
        move_id,
        line_id,
        warehouse_id,
        product_id,
        lot,
        expiration_date,
        quantity
    )
VALUES
    (96, 3, 2, 28, 'Z2025-03', CURRENT_DATE - INTERVAL '41 days', 1);

-- Adjust ID sequences to avoid duplicate key errors on inserts
SELECT
    setval (
        'user_id_seq',
        (
            SELECT
                MAX(id)
            FROM
                "user"
        )
    );

SELECT
    setval (
        'warehouse_id_seq',
        (
            SELECT
                MAX(id)
            FROM
                warehouse
        )
    );

SELECT
    setval (
        'product_category_id_seq',
        (
            SELECT
                MAX(id)
            FROM
                product_category
        )
    );

SELECT
    setval (
        'product_id_seq',
        (
            SELECT
                MAX(id)
            FROM
                product
        )
    );

SELECT
    setval (
        'stock_move_move_id_seq',
        (
            SELECT
                MAX(move_id)
            FROM
                stock_move
        )
    );