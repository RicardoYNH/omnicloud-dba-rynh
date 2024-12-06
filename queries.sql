-- queries.sql

-- 1. Lista de todos los pedidos junto con nombre del cliente y el producto en un rango de fechas.
SELECT orders.order_id, users.name AS customer_name, products.product_name, orders.order_date
FROM orders
JOIN users ON orders.user_id = users.user_id
JOIN products ON orders.product_id = products.product_id
WHERE orders.order_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY orders.order_date;

-- 2. Calcula el total de ventas por cliente.
SELECT users.name AS customer_name, SUM(products.product_price) AS total_sales
FROM orders
JOIN users ON orders.user_id = users.user_id
JOIN products ON orders.product_id = products.product_id
GROUP BY users.name
ORDER BY total_sales DESC;

-- 3. Encuentra a los 3 mejores clientes, que tengan el mayor gasto.
SELECT users.name AS customer_name, SUM(products.product_price) AS total_spent
FROM orders
JOIN users ON orders.user_id = users.user_id
JOIN products ON orders.product_id = products.product_id
GROUP BY users.name
ORDER BY total_spent DESC
LIMIT 3;

-- 4. Verifica que los índices de tus tablas estén siendo utilizados.
EXPLAIN ANALYZE SELECT * FROM users WHERE name = 'John Doe';
EXPLAIN ANALYZE SELECT * FROM products WHERE product_name = 'Laptop';
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- 5. Muestra los nombres de los clientes que no han realizado ningún pedido.
SELECT users.name AS customer_name
FROM users
LEFT JOIN orders ON users.user_id = orders.user_id
WHERE orders.order_id IS NULL;
