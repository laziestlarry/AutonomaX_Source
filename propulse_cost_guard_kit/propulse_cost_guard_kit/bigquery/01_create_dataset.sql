-- Creates a dataset in US (adjust location if needed, e.g., EU)
CREATE SCHEMA IF NOT EXISTS `propulse-autonomax.shopify_analytics`
OPTIONS(
  location='US',
  default_table_expiration_days=NULL,
  description='Shopify analytics dataset: partitioned tables for cost control'
);
