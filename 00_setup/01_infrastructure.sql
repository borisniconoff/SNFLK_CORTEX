-- ============================================================
-- 00_setup / 01_infrastructure.sql
-- Creates the database, schemas, warehouse and resource monitor
-- for the Instacart learning lab.
-- ============================================================
USE ROLE ACCOUNTADMIN;

-- 1) Database and layers
CREATE DATABASE IF NOT EXISTS INSTACART_LAB;
CREATE SCHEMA   IF NOT EXISTS INSTACART_LAB.RAW;      -- data exactly as it arrives
CREATE SCHEMA   IF NOT EXISTS INSTACART_LAB.STAGING;  -- cleaned, 1:1 with RAW
CREATE SCHEMA   IF NOT EXISTS INSTACART_LAB.MARTS;    -- business-ready models

-- 2) Warehouse (compute)
CREATE WAREHOUSE IF NOT EXISTS LAB_WH
  WAREHOUSE_SIZE      = 'XSMALL'  -- smallest size, enough for this project
  AUTO_SUSPEND        = 60        -- suspend after 60 seconds idle
  AUTO_RESUME         = TRUE      -- wake up automatically on the next query
  INITIALLY_SUSPENDED = TRUE;     -- no cost at creation time

-- 3) Resource monitor (credit budget for the warehouse)
CREATE OR REPLACE RESOURCE MONITOR LAB_MONITOR
  WITH CREDIT_QUOTA    = 10       -- monthly credit cap (adjust to taste)
       FREQUENCY       = MONTHLY
       START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 75  PERCENT DO NOTIFY             -- heads-up
    ON 100 PERCENT DO SUSPEND            -- let running queries finish, block new ones
    ON 110 PERCENT DO SUSPEND_IMMEDIATE; -- cancel everything, safety net

-- 4) Attach the monitor to the warehouse
ALTER WAREHOUSE LAB_WH SET RESOURCE_MONITOR = LAB_MONITOR;

-- 5) Working context
USE WAREHOUSE LAB_WH;
USE DATABASE  INSTACART_LAB;

-- 6) Verification
SHOW WAREHOUSES        LIKE 'LAB_WH';
SHOW RESOURCE MONITORS LIKE 'LAB_MONITOR';
SHOW SCHEMAS IN DATABASE INSTACART_LAB;

-- ------------------------------------------------------------
-- Optional: a dedicated role so day-to-day work does not use ACCOUNTADMIN
-- ------------------------------------------------------------
-- USE ROLE SECURITYADMIN;
-- CREATE ROLE IF NOT EXISTS LAB_ROLE;
-- GRANT ROLE LAB_ROLE TO USER <your_user>;
--
-- USE ROLE ACCOUNTADMIN;
-- GRANT USAGE, OPERATE ON WAREHOUSE LAB_WH TO ROLE LAB_ROLE;
-- GRANT ALL ON DATABASE INSTACART_LAB TO ROLE LAB_ROLE;
-- GRANT ALL ON ALL SCHEMAS IN DATABASE INSTACART_LAB TO ROLE LAB_ROLE;
-- GRANT ALL ON FUTURE SCHEMAS IN DATABASE INSTACART_LAB TO ROLE LAB_ROLE;
