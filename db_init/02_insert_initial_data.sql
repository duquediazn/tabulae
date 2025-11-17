-- Users for testing purposes (passwords: alice_example, bob_example, charlie_example)
INSERT INTO
    "user" (name, email, password, role, is_active)
VALUES
    (
        'Alice Smith',
        'alice@example.com',
        '$2a$12$h1YMx6rEJDJ6atDWydlVGObCgOPfrgB5YxGgLE1fqm3/ebWmGkMRm',
        'admin',
        true
    ),
    (
        'Bob Johnson',
        'bob@example.com',
        '$2a$12$OC4NtH.0NnLnJLLjNvUA2uRg34dgKVN8li3Zi8aBtDDLYI8rPY2ba',
        'user',
        true
    ),
    (
        'Charlie Lee',
        'charlie@example.com',
        '$2a$12$TCXanIk6qWqB79Byedo3SOE91oU3VVpA5mDBbdIvRWqGhY8Xd8/g.',
        'user',
        false
    );

-- Warehouses
INSERT INTO
    warehouse (description, is_active)
VALUES
    ('Main Warehouse', TRUE),
    ('North Store', TRUE),
    ('City Center Store', TRUE),
    ('South Outlet', FALSE);

-- Product Categories
INSERT INTO
    product_category (name)
VALUES
    ('Video Games'),
    ('Books'),
    ('Collectible Figures'),
    ('Board Games'),
    ('Merchandise');

INSERT INTO
    product (
        short_name,
        description,
        sku,
        category_id,
        is_active
    )
VALUES
    (
        'Zelda: Breath of the Wild',
        'Action-adventure game for Nintendo Switch',
        'ZELDA01',
        1,
        TRUE
    ),
    (
        'God of War Ragnarök',
        'Action game for PlayStation 5',
        'GOWR01',
        1,
        TRUE
    ),
    (
        '1984 by George Orwell',
        'Dystopian novel',
        'BOOK01',
        2,
        TRUE
    ),
    (
        'The Magic Book Vol. 1',
        'Fantasy book for young readers',
        'BOOK02',
        2,
        TRUE
    ),
    (
        'Iron Hero Funko Figure',
        'Limited edition collectible figure',
        'FIG01',
        3,
        TRUE
    ),
    (
        '1000-piece Puzzle',
        'Board game for the whole family',
        'BOARD01',
        4,
        TRUE
    ),
    (
        'Retro Game T-Shirt M',
        'Official themed T-shirt',
        'MERCH01',
        5,
        TRUE
    ),
    (
        'Football League 2024',
        'Multiplatform football video game',
        'FOOT24',
        1,
        TRUE
    ),
    (
        'The Little Prince',
        'Illustrated children’s book',
        'BOOK03',
        2,
        TRUE
    ),
    (
        'Wooden Chess Set',
        'Classic strategy board game',
        'CHESS01',
        4,
        TRUE
    ),
    (
        'Hogwarts Hoodie L',
        'Official fantasy-themed hoodie',
        'MERCH02',
        5,
        TRUE
    ),
    (
        'Grogu Funko Figure',
        'Collectible figure from space series',
        'FIG02',
        3,
        TRUE
    ),
    (
        'Catan',
        'Strategy board game',
        'BOARD02',
        4,
        TRUE
    ),
    (
        'Adventure Poster',
        'Decorative fantasy-themed poster',
        'MERCH03',
        5,
        TRUE
    ),
    (
        'Spider Hero 2',
        'PlayStation 5 exclusive action game',
        'SPIDER02',
        1,
        TRUE
    ),
    (
        'Limited Edition Trading Card',
        'Collectible card with special ink',
        'CARD01',
        3,
        TRUE
    ),
    (
        'Monthly Manga Magazine',
        'Serialized manga issue',
        'MANGA01',
        2,
        TRUE
    ),
    (
        'Trading Card Starter Pack',
        'Beginner set for collectible card game',
        'CARDPACK01',
        4,
        TRUE
    ),
    (
        'Zelda-themed Chewing Gum',
        'Promotional edible product',
        'GUM01',
        5,
        TRUE
    ),
    (
        'Surprise Box',
        'Random contents with expiration date',
        'BOX01',
        5,
        TRUE
    ),
    (
        'Mario Edible Figure',
        'Cake topper with expiration',
        'FOODFIG01',
        3,
        TRUE
    ),
    (
        'Geek Popcorn',
        'Limited edition themed snack',
        'SNACK01',
        5,
        TRUE
    ),
    (
        '2024 Fantasy Agenda',
        'Agenda with limited duration',
        'AGENDA01',
        2,
        TRUE
    ),
    (
        'Energy Drink – Lightning Edition',
        'Promo energy drink with expiration date',
        'ENERGY01',
        5,
        TRUE
    ),
    (
        'Card Pack – Duel Series',
        'Sealed collectible card product',
        'DUEL01',
        3,
        TRUE
    ),
    (
        'Collector’s Manual 2023',
        'Physical guide with limited content',
        'GUIDE01',
        2,
        TRUE
    ),
    (
        'One Piece Snack',
        'Geek-themed snack product',
        'SNACK02',
        5,
        TRUE
    ),
    (
        'Special Edition Magazine',
        'Exclusive release with publication date',
        'MAG01',
        2,
        TRUE
    ),
    (
        'Promotional Metal Tin',
        'Collectible tin with candy inside',
        'TIN01',
        5,
        TRUE
    ),
    (
        'Holiday Gift Box',
        'Seasonal limited-time product',
        'HOLIDAY01',
        5,
        TRUE
    );