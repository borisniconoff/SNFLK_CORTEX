"""Simulate one new day of orders: generate -> stage -> COPY INTO RAW.

Each run advances the simulated calendar by one day, so you can "move time forward"
whenever you want to practise incremental processing.

Usage (from the repository root):
    python run_daily_batch.py                 # 5,000 orders, next simulated day
    python run_daily_batch.py --orders 10000
    python run_daily_batch.py --dry-run       # generate the CSV files only, no upload
    python run_daily_batch.py --seed 42       # reproducible batch
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from common.snowflake_conn import get_connection
from data_generator.generate_batch import build_batch, write_batch
from data_generator.snowflake_state import fetch_state
from ingestion.load_batch import ensure_incremental_objects, upload_and_copy


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and load one simulated day of orders.")
    parser.add_argument("--orders", type=int, default=5000, help="Orders in the batch (default 5000)")
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        default=date(2026, 1, 1),
        help="First simulated day, used only when no batch exists yet (YYYY-MM-DD)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--out-dir", type=Path, default=Path("data/batches"))
    parser.add_argument("--dry-run", action="store_true", help="Write CSVs but do not upload")
    args = parser.parse_args()

    conn = get_connection()
    try:
        ensure_incremental_objects(conn)
        cur = conn.cursor()

        state = fetch_state(cur)
        sim_date = (
            args.start_date
            if state.last_order_date is None
            else state.last_order_date + timedelta(days=1)
        )
        batch_id = f"{sim_date:%Y%m%d}"

        rng = np.random.default_rng(args.seed)
        orders, lines = build_batch(state, args.orders, sim_date, batch_id, rng)
        orders_path, lines_path = write_batch(orders, lines, args.out_dir, batch_id)
        print(
            f"Batch {batch_id}: {len(orders):,} orders / {len(lines):,} lines "
            f"(order_id {orders.order_id.min()}..{orders.order_id.max()})"
        )
        print(f"Files: {orders_path}  |  {lines_path}")

        if args.dry_run:
            print("Dry run: nothing uploaded.")
            return

        results = upload_and_copy(cur, orders_path, lines_path)
        for name, rows in results.items():
            for row in rows:
                print(f"COPY {name}: {row}")

        cur.execute("SELECT COUNT(*) FROM ORDERS_INCREMENTAL WHERE batch_id = %s", (batch_id,))
        n_orders = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM ORDER_PRODUCTS_INCREMENTAL WHERE batch_id = %s", (batch_id,)
        )
        n_lines = cur.fetchone()[0]
        print(f"Loaded in Snowflake -> orders: {n_orders:,} | lines: {n_lines:,}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
