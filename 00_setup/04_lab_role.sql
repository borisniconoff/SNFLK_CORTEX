-- ============================================================
-- 00_setup / 04_lab_role.sql
-- Least-privilege role for day-to-day work in the lab.
-- Before running, replace <YOUR_USER> in the SET below (do not commit your user name).
-- ============================================================
SET lab_user = '<YOUR_USER>';

-- 1) Create the role and place it under SYSADMIN (recommended hierarchy)
USE ROLE SECURITYADMIN;
CREATE ROLE IF NOT EXISTS LAB_ROLE COMMENT = 'Day-to-day role for the Instacart learning lab';
GRANT ROLE LAB_ROLE TO ROLE SYSADMIN;
GRANT ROLE LAB_ROLE TO USER IDENTIFIER($lab_user);

-- Sessions use only the primary role, so permissions can be tested for real.
-- (With secondary roles ALL, a session also gets the privileges of all other roles.)
ALTER USER IDENTIFIER($lab_user) SET DEFAULT_SECONDARY_ROLES = ();

-- 2) Compute and database access
USE ROLE ACCOUNTADMIN;
GRANT USAGE, OPERATE ON WAREHOUSE LAB_WH TO ROLE LAB_ROLE;   -- use and start/stop, cannot resize
GRANT USAGE, CREATE SCHEMA ON DATABASE INSTACART_LAB TO ROLE LAB_ROLE;

-- 3) Hand over ownership of the lab schemas and what they contain (schema first)
GRANT OWNERSHIP ON SCHEMA INSTACART_LAB.RAW     TO ROLE LAB_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON SCHEMA INSTACART_LAB.STAGING TO ROLE LAB_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON SCHEMA INSTACART_LAB.MARTS   TO ROLE LAB_ROLE COPY CURRENT GRANTS;

GRANT OWNERSHIP ON ALL TABLES       IN SCHEMA INSTACART_LAB.RAW TO ROLE LAB_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON ALL STAGES       IN SCHEMA INSTACART_LAB.RAW TO ROLE LAB_ROLE COPY CURRENT GRANTS;
GRANT OWNERSHIP ON ALL FILE FORMATS IN SCHEMA INSTACART_LAB.RAW TO ROLE LAB_ROLE COPY CURRENT GRANTS;

-- 4) Needed from module 1 on: run tasks
GRANT EXECUTE TASK ON ACCOUNT TO ROLE LAB_ROLE;

-- 5) Verify
USE ROLE LAB_ROLE;
USE SECONDARY ROLES NONE;
USE WAREHOUSE LAB_WH;
SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();       -- LAB_ROLE and no secondary roles
SELECT COUNT(*) FROM INSTACART_LAB.RAW.ORDERS_INCREMENTAL;  -- rows loaded so far
SHOW GRANTS TO ROLE LAB_ROLE;