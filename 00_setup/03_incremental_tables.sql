-- ============================================================
-- 00_setup / 03_incremental_tables.sql
-- Stage and tables that receive the simulated daily batches.
-- run_daily_batch.py executes this file automatically (it is idempotent),
-- but you can also run it by hand in Snowsight.
-- ============================================================
USE SCHEMA INSTACART_LAB.RAW;

CREATE FILE FORMAT IF NOT EXISTS FF_CSV_INSTACART
  TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"' EMPTY_FIELD_AS_NULL = TRUE;

-- Landing zone for generated batches (sub-folders: orders/, order_products/)
CREATE STAGE IF NOT EXISTS STG_INCREMENTAL
  FILE_FORMAT = FF_CSV_INSTACART;

CREATE TABLE IF NOT EXISTS ORDERS_INCREMENTAL (
  order_id               NUMBER,
  user_id                NUMBER,
  eval_set               VARCHAR,
  order_number           NUMBER,
  order_dow              NUMBER,   -- 0 = Sunday ... 6 = Saturday (simulation convention)
  order_hour_of_day      NUMBER,
  days_since_prior_order NUMBER,
  order_date             DATE,     -- simulated calendar day
  batch_id               VARCHAR,  -- YYYYMMDD of the simulated day
  _loaded_at             TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS ORDER_PRODUCTS_INCREMENTAL (
  order_id          NUMBER,
  product_id        NUMBER,
  add_to_cart_order NUMBER,
  reordered         NUMBER,
  batch_id          VARCHAR,
  _loaded_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
