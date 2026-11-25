# CLAUDE.md

Working agreement for Claude Code in this repository (SNFLK_CORTEX).

## Project

A personal, portfolio-oriented learning lab for the modern Snowflake data-engineering stack
(Streams & Tasks, Dynamic Tables, dbt, Snowpark, Airflow, Cortex, Streamlit) on the Instacart
dataset plus synthetic daily batches. The goal is for Boris to learn, so the process matters
as much as the result. `README.md` describes the project; `PLAN.md` tracks progress.

## Role of Claude

- Default: reviewer and tutor. Boris writes the learning code himself (SQL, Python, dbt models,
  DAGs, Snowpark). When reviewing, give a hint first and script documentation. Give the full solution only when he asks for it.
- Claude may edit files in this repo. Documentation and housekeeping (`README.md`, `PLAN.md`,
  `CLAUDE.md`, `.gitignore`, configuration) can be edited directly. Learning code is edited only
  when Boris asks for it.
- Do not run `git commit` or `git push`, and do not run anything against Snowflake, unless Boris asks.
- Explain new terms with an analogy and simple graphic examples. Ask clarifying questions before building something large.

## Language

- Chat with Boris: Spanish.
- Code, SQL comments, commit messages, `README.md` and this file: English.
- `PLAN.md`: Spanish.

## Commands

```bash
pip install -r requirements.txt
pytest                                  # unit tests, no Snowflake connection needed
python run_daily_batch.py               # one simulated day: generate, stage, COPY INTO RAW
python run_daily_batch.py --dry-run     # generate the CSVs only
python run_daily_batch.py --seed 42     # reproducible batch
python -m ingestion.load_historical --data-dir <path-to-instacart>
```

Boris works on Windows (PowerShell): set environment variables with `$env:NAME = "value"`.

## Snowflake conventions

- Database `INSTACART_LAB`, schemas `RAW`, `STAGING`, `MARTS`.
- Work with `LAB_ROLE` and `USE SECONDARY ROLES NONE`, so permissions are tested for real.
- Compute on `LAB_WH` (XSMALL, `AUTO_SUSPEND = 60`, attached to a resource monitor).
- Fully qualify object names (`RAW.ORDERS_INCREMENTAL`, not `ORDERS_INCREMENTAL`).
- SQL scripts are run section by section in Snowsight, not "Run All"; say so in a comment
  at the top of any script that consumes a stream or resumes a task.
- A script must not depend on an object created by a later script. Order the files by dependency.
- Tasks are created suspended and stay suspended except while practising. Never leave a
  one-minute task resumed.
- Prefer explicit column lists over `SELECT *` when inserting.

## Security

- No credentials, tokens or keys in the repo. Use environment variables or git-ignored files
  (`.env`, `profiles.yml`).
- Never commit `data/` or any CSV or Parquet file.
- Do not put a real user name in SQL (`04_lab_role.sql` uses the `<YOUR_USER>` placeholder).

## PLAN.md rules

- `PLAN.md` is the source of truth for progress: done tasks ÷ total tasks.
- Mark a task `[x]` only if its evidence exists in the repo, and list that evidence.
- Keep the module numbering identical to `README.md` and to the branch names.
- When a task is split or added, record it in the change history at the bottom of `PLAN.md`.
- Update the status list in `README.md` when a module is finished.

## Git workflow

- One branch per module: `module-N/topic` (for example `module-1/streams-tasks`).
- Small commits with imperative English messages ("Add task that consumes the orders stream").
- Folder names follow `NN_topic` and are plural where the README says so (`01_streams_tasks`).
- When showing git commands, add a comment line above each command explaining what it does.
  Do not draw branch diagrams.