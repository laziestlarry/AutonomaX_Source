# GA4 → BigQuery Mapping (Starter)
- GA4 export tables: `events_*`
- Core fields → model table `analytics.events_flat`:
  - `event_date`, `event_name`, `user_pseudo_id`, `session_id`, `page_location`, `traffic_source`, `items` (repeated)
- Materialize:
  - `analytics.daily_kpis` (sessions, users, conv rate, revenue)
  - `analytics.product_perf` (item_id, item_name, add_to_cart, purchases, revenue)
