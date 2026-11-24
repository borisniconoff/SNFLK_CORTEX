# PLAN.md — Plan de aprendizaje Data Engineer

Fuente de verdad del avance. Avance = tareas hechas ÷ total de tareas.
Una tarea se marca `[x]` solo si su evidencia existe en el repo.
Última actualización: 2026-11-24

## Módulo 0: Snowflake (base)
- [x] Cargar dataset Instacart a Snowflake
  - Evidencia: `00_setup/02_load_instacart.sql`, `ingestion/load_historical.py`

## Módulo 1: dbt
- [ ] Instalar dbt y conectar a Snowflake
  - Evidencia esperada: proyecto dbt en el repo (`dbt_project.yml`, `profiles` sin credenciales)
- [ ] Modelos staging sobre Instacart
  - Evidencia esperada: carpeta `models/staging/` con modelos de orders, order_products, etc.
- [ ] Tests y documentación en dbt
  - Evidencia esperada: archivos `.yml` con tests y descripciones

## Módulo 2: Airflow
- [ ] Levantar Airflow con Docker
  - Evidencia esperada: `docker-compose.yml` de Airflow
- [ ] DAG de carga hacia Snowflake
  - Evidencia esperada: DAG en `dags/`
- [ ] Orquestar dbt desde Airflow
  - Evidencia esperada: DAG que ejecute dbt

## Módulo 3: Snowpark
- [ ] Primeros DataFrames con Snowpark
  - Evidencia esperada: script Python con Snowpark
- [ ] UDFs y stored procedures en Python
  - Evidencia esperada: UDF/SP registrados desde Python
- [ ] Pipeline de transformación con Snowpark
  - Evidencia esperada: pipeline en Snowpark y su prueba

## Módulo 4: Streams y Tasks
- [x] Streams sobre tabla de órdenes
  - Evidencia: `01_streams_tasks/01_streams.sql`
- [x] Tasks programadas y encadenadas
  - Evidencia: `01_streams_tasks/02_tasks.sql`
- [ ] Pipeline incremental con Streams + Tasks
  - Evidencia esperada: flujo end-to-end con `run_daily_batch.py` + streams + tasks, con prueba en `tests/`

## Módulo 5: Dynamic Tables
- [ ] Primera Dynamic Table
- [ ] Cadena de Dynamic Tables y target lag
- [ ] Comparar Dynamic Tables vs Streams + Tasks

## Módulo 6: Cortex
- [ ] Funciones LLM de Cortex (COMPLETE, SUMMARIZE)
- [ ] Cortex Search sobre productos
- [ ] App Streamlit con Cortex