-- Partitioned + clustered Orders table (skeleton)
CREATE TABLE IF NOT EXISTS `propulse-autonomax.shopify_analytics.orders_partitioned`
PARTITION BY DATE(order_created_at)
CLUSTER BY store_id, customer_id AS
SELECT * FROM `propulse-autonomax.shopify_analytics.orders_source` WHERE 1=0;
