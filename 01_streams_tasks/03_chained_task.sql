-- ============================================================
-- 01_streams_tasks / 03_chained_task.sql
-- Note: re-running the CREATE OR REPLACE TASK of 02_tasks.sql keeps the child's
--   dependency (the "predecessors" of the child still names the root, tested on
--   2026-11-25), but the new root starts suspended. Resume the child first and
--   the root last, and check SHOW TASKS afterwards.

-- Second task of the graph: summarises the consumed orders per batch.
--
--   ORDERS_INCREMENTAL_STREAM
--          |
--          v
--   CONSUME_ORDERS_TASK      (root task: has the SCHEDULE and the WHEN condition)
--          |  AFTER
--          v
--   SUMMARIZE_ORDERS_TASK    (child task: no SCHEDULE, runs when the root succeeds)
--          |
--          v
--   STAGING.ORDERS_BATCH_SUMMARY   (one row per batch_id)
--
-- Run section by section, not Run All.
-- Prerequisites: 01_streams.sql and 02_tasks.sql already ran
--   (stream, STAGING.ORDERS_CONSUMED and RAW.CONSUME_ORDERS_TASK exist).
-- Idempotent: the MERGE recomputes each batch, so running the child twice
--   never duplicates rows.
-- ============================================================
USE ROLE LAB_ROLE;
USE SECONDARY ROLES NONE;
USE WAREHOUSE LAB_WH;
USE DATABASE INSTACART_LAB;

-- 1) Target table: one row per simulated day (batch)
CREATE TABLE IF NOT EXISTS STAGING.ORDERS_BATCH_SUMMARY (
  batch_id       VARCHAR,
  order_date     DATE,
  orders_count   NUMBER,
  distinct_users NUMBER,
  _updated_at    TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 2) The graph can only be changed while the root task is suspended
ALTER TASK RAW.CONSUME_ORDERS_TASK SUSPEND;

-- 3) Child task: no SCHEDULE, it runs AFTER the root task finishes successfully.
--    If the root is skipped (stream empty, WHEN is false), the child does not run.
CREATE OR REPLACE TASK RAW.SUMMARIZE_ORDERS_TASK
  WAREHOUSE = 'LAB_WH'
  -- SUSPEND_TASK_AFTER_NUM_FAILURES = 3
  AFTER RAW.CONSUME_ORDERS_TASK
AS
  MERGE INTO STAGING.ORDERS_BATCH_SUMMARY AS t
  USING (
    SELECT batch_id,
           MIN(order_date)         AS order_date,
           COUNT(*)                AS orders_count,
           COUNT(DISTINCT user_id) AS distinct_users
    FROM STAGING.ORDERS_CONSUMED
    GROUP BY batch_id
  ) AS s
  ON t.batch_id = s.batch_id
  WHEN MATCHED THEN UPDATE SET
    t.order_date     = s.order_date,
    t.orders_count   = s.orders_count,
    t.distinct_users = s.distinct_users,
    t._updated_at    = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN INSERT (batch_id, order_date, orders_count, distinct_users)
    VALUES (s.batch_id, s.order_date, s.orders_count, s.distinct_users);

-- 4) Check the dependency: the "predecessors" column of the child must name the root
SHOW TASKS IN SCHEMA RAW;

-- 5) Resume: children first, root last
ALTER TASK RAW.SUMMARIZE_ORDERS_TASK RESUME;
ALTER TASK RAW.CONSUME_ORDERS_TASK RESUME;

-- 6) Test: in PowerShell run `python run_daily_batch.py`, wait 1-2 minutes, then run:
SELECT * FROM STAGING.ORDERS_BATCH_SUMMARY ORDER BY batch_id;

-- The two numbers must match
SELECT (SELECT SUM(orders_count) FROM STAGING.ORDERS_BATCH_SUMMARY) AS in_summary,
       (SELECT COUNT(*)          FROM STAGING.ORDERS_CONSUMED)      AS in_consumed;

-- Both tasks should appear, root first and child right after it
SELECT name, state, scheduled_time, completed_time, error_message
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(RESULT_LIMIT => 20))
WHERE name IN ('CONSUME_ORDERS_TASK', 'SUMMARIZE_ORDERS_TASK')
ORDER BY scheduled_time DESC;

-- 7) Idempotency test: run the MERGE of the child by hand (copy it from step 3)
--    twice. These numbers must be identical before and after each run.
SELECT COUNT(*) AS summary_rows, SUM(orders_count) AS summary_orders
FROM STAGING.ORDERS_BATCH_SUMMARY;

-- 8) When you finish practising, suspend everything (root first)
ALTER TASK RAW.CONSUME_ORDERS_TASK SUSPEND;
ALTER TASK RAW.SUMMARIZE_ORDERS_TASK SUSPEND;
SHOW TASKS IN SCHEMA RAW;
SELECT "name", "created_on", "predecessors", "state" FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));