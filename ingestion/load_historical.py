"""One-off historical load of the Instacart CSV files into INSTACART_LAB.RAW.

Usage (from the repository root):
    python -m ingestion.load_historical --data-dir C:\\data\\instacart

The script is idempotent: PUT skips files already in the stage and COPY INTO skips
files it already loaded, so running it twice does not duplicate data.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common.snowflake_conn import get_connection

FILE_FORMAT_DDL = """
CREATE FILE FORMAT IF NOT EXISTS FF_CSV_INSTACART
  TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"' EMPTY_FIELD_AS_NULL = TRUE
"""
STAGE_DDL = "CREATE STAGE IF NOT EXISTS STG_INSTACART FILE_FORMAT = FF_CSV_INSTACART"

# table -> (csv file name, column definitions)
TABLES: dict[str, tuple[str, str]] = {
    "AISLES": ("aisles.csv", "aisle_id NUMBER, aisle VARCHAR"),
    "DEPARTMENTS": ("departments.csv", "department_id NUMBER, department VARCHAR"),
    "PRODUCTS": (
        "products.csv",
        "product_id NUMBER, product_name VARCHAR, aisle_id NUMBER, department_id NUMBER",
    ),
    "ORDERS": (
        "orders.csv",
        "order_id NUMBER, user_id NUMBER, eval_set VARCHAR, order_number NUMBER, "
        "order_dow NUMBER, order_hour_of_day NUMBER, days_since_prior_order NUMBER",
    ),
    "ORDER_PRODUCTS_PRIOR": (
        "order_products__prior.csv",
        "order_id NUMBER, product_id NUMBER, add_to_cart_order NUMBER, reordered NUMBER",
    ),
    "ORDER_PRODUCTS_TRAIN": (
        "order_products__train.csv",
        "order_id NUMBER, product_id NUMBER, add_to_cart_order NUMBER, reordered NUMBER",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the Instacart CSV files into Snowflake.")
    parser.add_argument("--data-dir", required=True, type=Path, help="Folder with the CSV files")
    args = parser.parse_args()

    missing = [f for f, _ in TABLES.values() if not (args.data_dir / f).exists()]
    if missing:
        raise SystemExit(f"Missing files in {args.data_dir}: {', '.join(missing)}")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(FILE_FORMAT_DDL)
        cur.execute(STAGE_DDL)

        for table, (csv_name, columns) in TABLES.items():
            local = (args.data_dir / csv_name).resolve().as_posix()
            print(f"[{table}] uploading {csv_name} ...")
            cur.execute(
                f"PUT 'file://{local}' @STG_INSTACART AUTO_COMPRESS=TRUE PARALLEL=4"
            )
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
            cur.execute(
                f"COPY INTO {table} FROM @STG_INSTACART "
                f"FILES = ('{csv_name}.gz') ON_ERROR = 'ABORT_STATEMENT'"
            )
            for row in cur.fetchall():
                print(f"[{table}] copy result: {row}")

        print("\nRow counts:")
        for table in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table:<22} {cur.fetchone()[0]:>12,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
