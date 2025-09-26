-- Partitioned + clustered Products table (skeleton)
CREATE TABLE IF NOT EXISTS `propulse-autonomax.shopify_analytics.products_partitioned`
PARTITION BY DATE(updated_at)
CLUSTER BY store_id, product_id AS
SELECT * FROM `propulse-autonomax.shopify_analytics.products_source` WHERE 1=0;
