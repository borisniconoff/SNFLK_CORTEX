# Snowflake Learning Lab (SNFLK_CORTEX)

A hands-on, portfolio-oriented project to go beyond everyday SQL and stored procedures in Snowflake
and practice the modern data-engineering stack end to end on a retail-style dataset.

## Goals

Build one cohesive pipeline while learning, in order:

| # | Module | Topic |
|---|--------|-------|
| 0 | Setup | Database, schemas, warehouse, resource monitor, data load |
| 1 | Streams & Tasks | Incremental processing with change tracking |
| 2 | Dynamic Tables | Declarative pipelines with target lag |
| 3 | dbt | Staging, marts, tests, docs, incremental models, snapshots |
| 4 | Snowpark | Python DataFrames, UDFs and procedures running inside Snowflake |
| 5 | Airflow | Orchestration of the whole pipeline |
| 6 | Cortex | AI functions, Cortex Search and Analyst on top of the data |
| 7 | Streamlit | Dashboard in Streamlit in Snowflake |

## Data

- **Instacart Market Basket Analysis** (Kaggle): orders, products, aisles, departments.
- **Synthetic data** generated with Python + Faker to simulate new orders arriving over time
  (used for incremental pipelines).

The raw data is **not** included in this repository. Download the Instacart files from Kaggle
(you need a free account and to accept the competition rules) and follow `00_setup/02_load_instacart.sql`.

## Repository layout

```
00_setup/          Infrastructure, data-loading and incremental-table SQL
01_streams_tasks/  Stream on the incremental orders table and the tasks that consume it
02_dynamic_tables/
03_dbt_project/
04_snowpark/
05_airflow/
06_cortex/
07_streamlit_app/
common/            Snowflake connection helper (env-var based)
data_generator/    Synthetic daily batch generator (pure, unit-tested)
ingestion/         Historical loader and per-batch loader
tests/             pytest unit tests
run_daily_batch.py One command = one simulated day of new orders
PLAN.md            Learning plan and progress tracker (written in Spanish)
CLAUDE.md          Working agreement for Claude Code in this repo
```

## Quick start

```bash
pip install -r requirements.txt

# Connection settings (PowerShell: $env:NAME = "value")
export SNOWFLAKE_ACCOUNT=<org-account>
export SNOWFLAKE_USER=<user>
# Password and MFA code are prompted if not set. For automation use
# SNOWFLAKE_PRIVATE_KEY_PATH (key-pair auth) instead.

# 1) One-off historical load (idempotent)
python -m ingestion.load_historical --data-dir /path/to/instacart

# 2) Simulate a new day: generates 5,000 orders, stages them and COPYs them into RAW
python run_daily_batch.py
python run_daily_batch.py --orders 10000 --seed 42   # other volume / reproducible
python run_daily_batch.py --dry-run                  # generate CSVs only

# 3) Tests (no Snowflake connection needed)
pytest
```

### How the incremental load works

Each run reads the current state from Snowflake (highest `order_id`, last `order_number`
per customer, product popularity, last simulated date), generates a batch for the next
simulated day, uploads it with unique file names to `@STG_INCREMENTAL`, and runs
`COPY INTO`. `COPY INTO` keeps load metadata, so a staged file is never loaded twice.

### Module 1: Streams & Tasks

Run the scripts in `01_streams_tasks/` in order, section by section (not "Run All"):

1. `01_streams.sql` creates an append-only stream on `RAW.ORDERS_INCREMENTAL`, so every new
   batch shows up as change records, and shows how to consume it into `STAGING.ORDERS_CONSUMED`.
2. `02_tasks.sql` creates `RAW.CONSUME_ORDERS_TASK`, which checks the stream every minute
   (`SYSTEM$STREAM_HAS_DATA`) and only runs when there are new rows.
3. `03_chained_task.sql` adds `RAW.SUMMARIZE_ORDERS_TASK`, a child task (`AFTER` the first one)
   that keeps one summary row per batch in `STAGING.ORDERS_BATCH_SUMMARY` using an idempotent `MERGE`.

Simulate a new day with `python run_daily_batch.py` and watch the stream and the task pick it up.

## Cost safety

All compute runs on an `XSMALL` warehouse with `AUTO_SUSPEND = 60` and is attached to a
monthly **resource monitor** that notifies at 75% and suspends at 100% of the credit quota.
See `00_setup/01_infrastructure.sql`.

> Resource monitors only track warehouse credits. Serverless features (serverless tasks, Cortex AI)
> are tracked and limited separately.

Tasks are created suspended. Resume a task only while practising and suspend it afterwards
(`ALTER TASK ... SUSPEND`), so a one-minute schedule does not keep waking the warehouse.

## Security

No credentials are stored in this repo. Use environment variables or a local, git-ignored
`.env` / `profiles.yml`.

## Status

Detailed progress, with the evidence for each item, lives in [`PLAN.md`](PLAN.md).

- [x] 00 Setup (infrastructure, historical load and daily batch loader)
- [x] 01 Streams & Tasks (in progress: stream, consumer task and chained task done; end-to-end test pending)
- [ ] 02 Dynamic Tables
- [ ] 03 dbt
- [ ] 04 Snowpark
- [ ] 05 Airflow
- [ ] 06 Cortex
- [ ] 07 Streamlit

## Disclaimer

This is a personal learning project. It uses only public and synthetic data and is unrelated
to any employer or client.