-- ============================================================
-- 00_setup / 02_load_instacart.sql
-- Loads the Instacart Market Basket CSV files into INSTACART_LAB.RAW
-- through an internal stage.
--
-- Source files (Kaggle competition "Instacart Market Basket Analysis"):
--   aisles.csv, departments.csv, products.csv, orders.csv,
--   order_products__prior.csv, order_products__train.csv
-- The data is NOT stored in this repository (see README).
-- ============================================================
USE ROLE ACCOUNTADMIN;      -- or LAB_ROLE if you created it
USE WAREHOUSE LAB_WH;
USE SCHEMA INSTACART_LAB.RAW;

-- 1) File format shared by all the CSV files
CREATE OR REPLACE FILE FORMAT FF_CSV_INSTACART
  TYPE                         = CSV
  FIELD_DELIMITER              = ','
  SKIP_HEADER                  = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'   -- product names can contain commas
  EMPTY_FIELD_AS_NULL          = TRUE;

-- 2) Internal named stage (a "loading dock" inside Snowflake)
CREATE STAGE IF NOT EXISTS STG_INSTACART
  FILE_FORMAT = FF_CSV_INSTACART;

-- 3) Upload the files to the stage. Pick ONE of these options:
--
--   Option A - Snowsight (UI): Catalog/Data > Databases > INSTACART_LAB > RAW
--              > Stages > STG_INSTACART > "+ Files".
--              Limit: 250 MB per file, so order_products__prior.csv does NOT fit.
--
--   Option B - SnowSQL (works for large files; compresses and splits automatically):
--       snowsql -a <account_identifier> -u <user>
--       USE SCHEMA INSTACART_LAB.RAW;
--       -- Windows:
--       PUT file://C:\data\instacart\*.csv @STG_INSTACART AUTO_COMPRESS=TRUE PARALLEL=4;
--       -- macOS / Linux:
--       PUT file:///Users/<you>/data/instacart/*.csv @STG_INSTACART AUTO_COMPRESS=TRUE PARALLEL=4;

-- 4) Check what landed in the stage
LIST @STG_INSTACART;

-- 5) Target tables
CREATE OR REPLACE TABLE AISLES (
  aisle_id NUMBER,
  aisle    VARCHAR
);

CREATE OR REPLACE TABLE DEPARTMENTS (
  department_id NUMBER,
  department    VARCHAR
);

CREATE OR REPLACE TABLE PRODUCTS (
  product_id    NUMBER,
  product_name  VARCHAR,
  aisle_id      NUMBER,
  department_id NUMBER
);

CREATE OR REPLACE TABLE ORDERS (
  order_id               NUMBER,
  user_id                NUMBER,
  eval_set               VARCHAR,
  order_number           NUMBER,
  order_dow              NUMBER,   -- day of week, 0-6
  order_hour_of_day      NUMBER,   -- 0-23
  days_since_prior_order NUMBER    -- NULL on a customer's first order
);

CREATE OR REPLACE TABLE ORDER_PRODUCTS_PRIOR (
  order_id          NUMBER,
  product_id        NUMBER,
  add_to_cart_order NUMBER,
  reordered         NUMBER
);

CREATE OR REPLACE TABLE ORDER_PRODUCTS_TRAIN LIKE ORDER_PRODUCTS_PRIOR;

-- 6) Load: stage -> tables
COPY INTO AISLES               FROM @STG_INSTACART PATTERN = '.*aisles\\.csv.*'                ON_ERROR = 'ABORT_STATEMENT';
COPY INTO DEPARTMENTS          FROM @STG_INSTACART PATTERN = '.*departments\\.csv.*'           ON_ERROR = 'ABORT_STATEMENT';
COPY INTO PRODUCTS             FROM @STG_INSTACART PATTERN = '.*products\\.csv.*'              ON_ERROR = 'ABORT_STATEMENT';
COPY INTO ORDERS               FROM @STG_INSTACART PATTERN = '.*orders\\.csv.*'                ON_ERROR = 'ABORT_STATEMENT';
COPY INTO ORDER_PRODUCTS_PRIOR FROM @STG_INSTACART PATTERN = '.*order_products__prior\\.csv.*' ON_ERROR = 'ABORT_STATEMENT';
COPY INTO ORDER_PRODUCTS_TRAIN FROM @STG_INSTACART PATTERN = '.*order_products__train\\.csv.*' ON_ERROR = 'ABORT_STATEMENT';

-- 7) Sanity checks (approximate reference counts for the public dataset)
SELECT 'AISLES'               AS tbl, COUNT(*) AS n FROM AISLES               -- ~134
UNION ALL SELECT 'DEPARTMENTS',          COUNT(*) FROM DEPARTMENTS          -- ~21
UNION ALL SELECT 'PRODUCTS',             COUNT(*) FROM PRODUCTS             -- ~49,688
UNION ALL SELECT 'ORDERS',               COUNT(*) FROM ORDERS               -- ~3.4 M
UNION ALL SELECT 'ORDER_PRODUCTS_PRIOR', COUNT(*) FROM ORDER_PRODUCTS_PRIOR -- ~32.4 M
UNION ALL SELECT 'ORDER_PRODUCTS_TRAIN', COUNT(*) FROM ORDER_PRODUCTS_TRAIN;-- ~1.4 M
