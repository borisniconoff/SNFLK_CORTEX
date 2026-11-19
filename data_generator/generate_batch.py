"""Synthetic daily batch generator for the Instacart lab.

The Instacart dataset is historical and static, so "new" data has to be simulated.
Instead of inventing values from scratch, a batch is sampled from the real
distributions already loaded in Snowflake:

* customers are real ``user_id`` values; each one gets its next ``order_number``
* products are drawn with probability proportional to how often they were bought
* basket size, hour of day and days-since-prior-order follow simple distributions

This module is pure (no Snowflake imports) so it can be unit-tested offline.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

ORDER_COLUMNS = [
    "order_id",
    "user_id",
    "eval_set",
    "order_number",
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order",
    "order_date",
    "batch_id",
]
LINE_COLUMNS = ["order_id", "product_id", "add_to_cart_order", "reordered", "batch_id"]

REORDER_PROBABILITY = 0.59  # roughly the share of reordered lines in Instacart
MEAN_BASKET_SIZE = 9


@dataclass(frozen=True)
class BatchState:
    """What the generator needs to know about the data that already exists."""

    next_order_id: int
    user_last_order_number: pd.Series  # index: user_id, value: highest order_number so far
    product_ids: np.ndarray
    product_weights: np.ndarray  # purchase counts (need not be normalised)
    last_order_date: Optional[date]  # None until the first batch is loaded


def _hour_distribution() -> np.ndarray:
    hours = np.arange(24)
    p = np.exp(-0.5 * ((hours - 13) / 4.0) ** 2)  # peak early afternoon
    return p / p.sum()


def build_batch(
    state: BatchState,
    n_orders: int,
    sim_date: date,
    batch_id: str,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(orders, order_lines)`` for one simulated day.

    Each customer places at most one order per batch.
    Day-of-week convention for the simulation: 0 = Sunday ... 6 = Saturday.
    """
    users = state.user_last_order_number
    if n_orders <= 0:
        raise ValueError("n_orders must be positive")
    if n_orders > len(users):
        raise ValueError(f"n_orders ({n_orders}) exceeds the number of customers ({len(users)})")

    chosen_users = rng.choice(users.index.to_numpy(), size=n_orders, replace=False)
    order_ids = np.arange(state.next_order_id, state.next_order_id + n_orders, dtype=np.int64)

    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "user_id": chosen_users.astype(np.int64),
            "eval_set": "new",
            "order_number": users.loc[chosen_users].to_numpy().astype(np.int64) + 1,
            "order_dow": (sim_date.weekday() + 1) % 7,
            "order_hour_of_day": rng.choice(24, size=n_orders, p=_hour_distribution()),
            "days_since_prior_order": np.minimum(rng.geometric(0.12, size=n_orders), 30),
            "order_date": sim_date.isoformat(),
            "batch_id": batch_id,
        }
    )[ORDER_COLUMNS]

    # Baskets: sample products with replacement, then drop repeats inside an order.
    sizes = np.clip(rng.poisson(MEAN_BASKET_SIZE, size=n_orders) + 1, 1, 40)
    probs = state.product_weights / state.product_weights.sum()
    picked = rng.choice(len(state.product_ids), size=int(sizes.sum()), p=probs)

    lines = pd.DataFrame(
        {
            "order_id": np.repeat(order_ids, sizes),
            "product_id": state.product_ids[picked].astype(np.int64),
        }
    )
    lines = lines.drop_duplicates(["order_id", "product_id"]).reset_index(drop=True)
    lines["add_to_cart_order"] = lines.groupby("order_id").cumcount() + 1
    lines["reordered"] = rng.binomial(1, REORDER_PROBABILITY, size=len(lines))
    lines["batch_id"] = batch_id

    return orders, lines[LINE_COLUMNS]


def write_batch(
    orders: pd.DataFrame, lines: pd.DataFrame, out_dir: Path, batch_id: str
) -> tuple[Path, Path]:
    """Write the batch as CSV files (with header) and return their paths."""
    out_dir = Path(out_dir) / batch_id
    out_dir.mkdir(parents=True, exist_ok=True)
    orders_path = out_dir / f"orders_{batch_id}.csv"
    lines_path = out_dir / f"order_products_{batch_id}.csv"
    orders.to_csv(orders_path, index=False)
    lines.to_csv(lines_path, index=False)
    return orders_path, lines_path
