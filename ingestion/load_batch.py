"""Upload one generated batch to the internal stage and COPY it into RAW."""
from __future__ import annotations

from pathlib import Path

SETUP_SQL = Path(__file__).resolve().parents[1] / "00_setup" / "03_incremental_tables.sql"

ORDERS_COPY = """
COPY INTO ORDERS_INCREMENTAL
  (order_id, user_id, eval_set, order_number, order_dow, order_hour_of_day,
   days_since_prior_order, order_date, batch_id)
FROM @STG_INCREMENTAL/orders/
FILE_FORMAT = (FORMAT_NAME = 'FF_CSV_INSTACART')
ON_ERROR = 'ABORT_STATEMENT'
"""

LINES_COPY = """
COPY INTO ORDER_PRODUCTS_INCREMENTAL
  (order_id, product_id, add_to_cart_order, reordered, batch_id)
FROM @STG_INCREMENTAL/order_products/
FILE_FORMAT = (FORMAT_NAME = 'FF_CSV_INSTACART')
ON_ERROR = 'ABORT_STATEMENT'
"""


def ensure_incremental_objects(conn) -> None:
    """Create the incremental stage and tables if they do not exist yet."""
    conn.execute_string(SETUP_SQL.read_text(encoding="utf-8"))


def _put(cur, local_path: Path, stage_folder: str) -> None:
    # as_posix() gives C:/path/file.csv on Windows, which PUT accepts.
    cur.execute(
        f"PUT 'file://{Path(local_path).resolve().as_posix()}' @STG_INCREMENTAL/{stage_folder}/ "
        "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
    )


def upload_and_copy(cur, orders_path: Path, lines_path: Path) -> dict[str, list]:
    """PUT both files and COPY them in.

    COPY INTO remembers which staged files it already loaded (load metadata), so
    re-running never duplicates a file that was loaded before.
    """
    _put(cur, orders_path, "orders")
    _put(cur, lines_path, "order_products")

    cur.execute(ORDERS_COPY)
    orders_result = cur.fetchall()
    cur.execute(LINES_COPY)
    lines_result = cur.fetchall()
    return {"orders": orders_result, "order_products": lines_result}
