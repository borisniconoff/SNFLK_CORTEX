"""Reads the current state of the lab data from Snowflake for the batch generator."""
from __future__ import annotations

import numpy as np
import pandas as pd

from data_generator.generate_batch import BatchState


def fetch_state(cur) -> BatchState:
    """Query Snowflake (historical + incremental tables) and build a BatchState."""
    cur.execute(
        """
        SELECT COALESCE(MAX(order_id), 0)
        FROM (SELECT order_id FROM ORDERS
              UNION ALL
              SELECT order_id FROM ORDERS_INCREMENTAL)
        """
    )
    next_order_id = int(cur.fetchone()[0]) + 1

    cur.execute("SELECT MAX(order_date) FROM ORDERS_INCREMENTAL")
    last_order_date = cur.fetchone()[0]  # datetime.date or None

    cur.execute(
        """
        SELECT user_id, MAX(order_number)
        FROM (SELECT user_id, order_number FROM ORDERS
              UNION ALL
              SELECT user_id, order_number FROM ORDERS_INCREMENTAL)
        GROUP BY user_id
        """
    )
    rows = cur.fetchall()
    user_last = pd.Series(
        [int(r[1]) for r in rows],
        index=pd.Index([int(r[0]) for r in rows], name="user_id"),
    )

    cur.execute("SELECT product_id, COUNT(*) FROM ORDER_PRODUCTS_PRIOR GROUP BY product_id")
    prod = cur.fetchall()
    product_ids = np.array([int(r[0]) for r in prod], dtype=np.int64)
    product_weights = np.array([float(r[1]) for r in prod], dtype=np.float64)

    return BatchState(
        next_order_id=next_order_id,
        user_last_order_number=user_last,
        product_ids=product_ids,
        product_weights=product_weights,
        last_order_date=last_order_date,
    )
