-- ENTITIES
CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    street_name TEXT NOT NULL,
    home_number TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    country TEXT
);
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL
);
CREATE TABLE user_account (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    phone_nb TEXT,
    hashed_pwd TEXT NOT NULL
);
CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    firstname TEXT NOT NULL,
    works_at_pizzeria_id INTEGER DEFAULT NULL,
    user_account_id INTEGER,
    address_id INTEGER NOT NULL,
    role_id INTEGER
);
CREATE TABLE bill (
    id SERIAL PRIMARY KEY,
    emission_date DATE NOT NULL,
    total_amout_ati NUMERIC(4, 2) NOT NULL,
    order_id INTEGER NOT NULL
);
CREATE TABLE order_status (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL
);
CREATE TABLE taken_order (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    address_id INTEGER NOT NULL,
    bill_id INTEGER,
    status_id INTEGER NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE
);
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    barcode TEXT NOT NULL,
    gram_weight INTEGER NOT NULL,
    unit_price_ati NUMERIC(4, 2) NOT NULL
);
CREATE TABLE pizzeria (
    id SERIAL PRIMARY KEY,
    name TEXT,
    phone_nb TEXT NOT NULL,
    address_id INTEGER
);
CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL
);
CREATE TABLE catalog_item (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    picture_file TEXT,
    unit_price_ati NUMERIC(4, 2) NOT NULL,
    is_available BOOLEAN,
    is_displayed BOOLEAN,
    recipe_id INTEGER,
    product_id INTEGER -- a catalog_item may be a product with no recipe (sodas, etc.)
);
CREATE TABLE keyword (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
-- ASSOCIATIVE ENTITIES
CREATE TABLE has_permission_to (
    role_id INTEGER REFERENCES role NOT NULL,
    permission_id INTEGER REFERENCES permission NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);
CREATE TABLE contains_item (
    order_id INTEGER REFERENCES taken_order NOT NULL,
    item_id INTEGER REFERENCES catalog_item NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price_ati NUMERIC(4, 2) NOT NULL,
    PRIMARY KEY (order_id, item_id)
);
CREATE TABLE has_product_in_stock (
    pizzeria_id INTEGER REFERENCES pizzeria NOT NULL,
    product_id INTEGER REFERENCES product NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (pizzeria_id, product_id)
);
CREATE TABLE requires_product (
    recipe_id INTEGER REFERENCES recipe NOT NULL,
    product_id INTEGER REFERENCES product NOT NULL,
    gram_amount INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, product_id)
);
CREATE TABLE has_keyword (
    item_id INTEGER REFERENCES catalog_item NOT NULL,
    keyword_id INTEGER REFERENCES keyword NOT NULL,
    PRIMARY KEY (item_id, keyword_id)
);
-- FOREIGN CONSTRAINTS
ALTER TABLE member
    ADD CONSTRAINT fk_member_user_account
    FOREIGN KEY (user_account_id)
    REFERENCES user_account (id);
ALTER TABLE member
    ADD CONSTRAINT fk_member_pizzeria
    FOREIGN KEY (works_at_pizzeria_id)
    REFERENCES pizzeria (id);
ALTER TABLE member
    ADD CONSTRAINT fk_member_address
    FOREIGN KEY (address_id)
    REFERENCES address (id);
ALTER TABLE user_account
    ADD CONSTRAINT fk_user_account_member
    FOREIGN KEY (member_id)
    REFERENCES member (id);
ALTER TABLE taken_order
    ADD CONSTRAINT fk_order_member
    FOREIGN KEY (member_id)
    REFERENCES member (id);
ALTER TABLE taken_order
    ADD CONSTRAINT fk_order_bill
    FOREIGN KEY (bill_id)
    REFERENCES bill (id);
ALTER TABLE taken_order
    ADD CONSTRAINT fk_order_status
    FOREIGN KEY (status_id)
    REFERENCES order_status (id);
ALTER TABLE taken_order
    ADD CONSTRAINT fk_order_address
    FOREIGN KEY (address_id)
    REFERENCES address (id);
ALTER TABLE bill
    ADD CONSTRAINT fk_bill_order
    FOREIGN KEY (order_id)
    REFERENCES taken_order (id);
ALTER TABLE pizzeria
    ADD CONSTRAINT fk_pizzeria_address
    FOREIGN KEY (address_id)
    REFERENCES address (id);
ALTER TABLE catalog_item
    ADD CONSTRAINT fk_catalog_item_recipe
    FOREIGN KEY (recipe_id)
    REFERENCES recipe (id);
ALTER TABLE catalog_item
    ADD CONSTRAINT fk_catalog_item_product
    FOREIGN KEY (product_id)
    REFERENCES product (id);
