# PLAN.md — Plan de aprendizaje Data Engineer

Fuente de verdad del avance. Avance = tareas hechas ÷ total de tareas.
Una tarea se marca `[x]` solo si su evidencia existe en el repo.
El orden de los módulos es el mismo que el de `README.md` y el de las ramas (`module-N/...`).
Última actualización: 2026-11-24
**Avance: 6 / 24 tareas (25%)**

## Módulo 0: Setup (base)
- [x] Infraestructura y rol de trabajo
  - Evidencia: `00_setup/01_infrastructure.sql`, `00_setup/04_lab_role.sql`
- [x] Cargar dataset Instacart a Snowflake
  - Evidencia: `00_setup/02_load_instacart.sql`, `ingestion/load_historical.py`
- [x] Generador y cargador de lotes diarios incrementales
  - Evidencia: `run_daily_batch.py`, `data_generator/`, `ingestion/load_batch.py`, `00_setup/03_incremental_tables.sql`, `tests/test_generate_batch.py`

## Módulo 1: Streams y Tasks
- [x] Stream sobre la tabla de órdenes
  - Evidencia: `01_streams_tasks/01_streams.sql`
- [x] Task programada que consume el stream hacia `STAGING.ORDERS_CONSUMED`
  - Evidencia: `01_streams_tasks/02_tasks.sql`
- [x] Segunda task encadenada con `AFTER` (resumen por `batch_id`)
  - Evidencia: `01_streams_tasks/03_chained_task.sql` (task hija con `AFTER` y tabla `STAGING.ORDERS_BATCH_SUMMARY`). Verificado el 2026-11-25: el resumen suma 20,000 órdenes, igual que `ORDERS_CONSUMED`, y el `MERGE` es idempotente
- [ ] Pipeline incremental end-to-end con Streams + Tasks
  - Evidencia esperada: flujo con `run_daily_batch.py` + stream + tasks encadenadas, con prueba en `tests/`

## Módulo 2: Dynamic Tables
- [ ] Primera Dynamic Table
  - Evidencia esperada: SQL en `02_dynamic_tables/`
- [ ] Cadena de Dynamic Tables y target lag
  - Evidencia esperada: SQL en `02_dynamic_tables/` con al menos dos tablas encadenadas
- [ ] Comparar Dynamic Tables vs Streams + Tasks
  - Evidencia esperada: nota de comparación en `02_dynamic_tables/`

## Módulo 3: dbt
- [ ] Instalar dbt y conectar a Snowflake
  - Evidencia esperada: proyecto dbt en `03_dbt_project/` (`dbt_project.yml`, `profiles` sin credenciales)
- [ ] Modelos staging sobre Instacart
  - Evidencia esperada: carpeta `models/staging/` con modelos de orders, order_products, etc.
- [ ] Tests y documentación en dbt
  - Evidencia esperada: archivos `.yml` con tests y descripciones

## Módulo 4: Snowpark
- [ ] Primeros DataFrames con Snowpark
  - Evidencia esperada: script Python con Snowpark en `04_snowpark/`
- [ ] UDFs y stored procedures en Python
  - Evidencia esperada: UDF/SP registrados desde Python
- [ ] Pipeline de transformación con Snowpark
  - Evidencia esperada: pipeline en Snowpark y su prueba

## Módulo 5: Airflow
- [ ] Levantar Airflow con Docker
  - Evidencia esperada: `docker-compose.yml` de Airflow en `05_airflow/`
- [ ] DAG de carga hacia Snowflake
  - Evidencia esperada: DAG en `dags/`
- [ ] Orquestar dbt desde Airflow
  - Evidencia esperada: DAG que ejecute dbt

## Módulo 6: Cortex
- [ ] Funciones LLM de Cortex (COMPLETE, SUMMARIZE)
  - Evidencia esperada: SQL en `06_cortex/`
- [ ] Cortex Search sobre productos
  - Evidencia esperada: servicio de búsqueda creado desde SQL en `06_cortex/`
- [ ] Cortex Analyst sobre los datos
  - Evidencia esperada: modelo semántico en `06_cortex/`

## Módulo 7: Streamlit
- [ ] Dashboard en Streamlit in Snowflake
  - Evidencia esperada: app en `07_streamlit_app/`
- [ ] App Streamlit con Cortex
  - Evidencia esperada: la app llama funciones de Cortex

## Historial de cambios
- 2026-11-24: se alineó la numeración con `README.md` (Streams y Tasks pasa a módulo 1). "Tasks programadas y encadenadas" se dividió en dos tareas: la task consumidora está hecha; la task encadenada con `AFTER` sigue pendiente. Se agregaron al módulo 0 la infraestructura y el generador de lotes (ya existían en el repo pero no estaban en el plan), Cortex Analyst y el módulo 7 (Streamlit), que estaban en el README pero no en el plan.
- 2026-11-25: se completó la segunda task encadenada (`03_chained_task.sql`) y se verificó que el resumen coincide con `ORDERS_CONSUMED`. Avance: 6 / 24.