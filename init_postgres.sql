-- init_postgres.sql
-- Crear la base de datos normalizada

-- Tabla de usuarios (anteriormente clientes)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    email TEXT
);

-- Tabla de productos
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT UNIQUE,
    product_price NUMERIC
);

-- Tabla de pedidos
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    order_date TIMESTAMP
);

-- Insertar datos en las tablas normalizadas
INSERT INTO users (name, email) VALUES
    ('John Doe', 'john.doe@original.com'),
    ('Jane Smith', 'jane.smith@original.com'),
    ('Alice Johnson', 'alice.johnson@original.com'),
    ('Bob Brown', 'bob.brown@original.com'),
    ('Carol White', 'carol.white@original.com');

INSERT INTO products (product_name, product_price) VALUES
    ('Laptop', 1200.50),
    ('Smartphone', 800.75),
    ('Tablet', 300.00),
    ('Monitor', 150.99),
    ('Keyboard', 50.00);

INSERT INTO orders (user_id, product_id, order_date) VALUES
    (1, 1, '2024-01-01 10:00:00'),
    (2, 2, '2024-01-02 11:30:00'),
    (3, 3, '2024-01-03 15:45:00'),
    (4, 4, '2024-01-04 09:20:00'),
    (5, 5, '2024-01-05 14:10:00');

-- Crear índices para optimizar consultas
CREATE INDEX idx_user_name ON users (name);
CREATE INDEX idx_product_name ON products (product_name);
CREATE INDEX idx_order_date ON orders (order_date);
CREATE INDEX idx_user_email ON users (email);
