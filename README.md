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
00_setup/          Infrastructure and data-loading SQL
01_streams_tasks/
02_dynamic_tables/
03_dbt_project/
04_snowpark/
05_airflow/
06_cortex/
07_streamlit_app/
data_generator/    Faker-based order generator
```

## Cost safety

All compute runs on an `XSMALL` warehouse with `AUTO_SUSPEND = 60` and is attached to a
monthly **resource monitor** that notifies at 75% and suspends at 100% of the credit quota.
See `00_setup/01_infrastructure.sql`.

> Resource monitors only track warehouse credits. Serverless features (serverless tasks, Cortex AI)
> are tracked and limited separately.

## Security

No credentials are stored in this repo. Use environment variables or a local, git-ignored
`.env` / `profiles.yml`.

## Status

- [ ] 00 Setup
- [ ] 01 Streams & Tasks
- [ ] 02 Dynamic Tables
- [ ] 03 dbt
- [ ] 04 Snowpark
- [ ] 05 Airflow
- [ ] 06 Cortex
- [ ] 07 Streamlit

## Disclaimer

This is a personal learning project. It uses only public and synthetic data and is unrelated
to any employer or client.
