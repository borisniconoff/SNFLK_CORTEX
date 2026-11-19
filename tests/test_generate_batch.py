from datetime import date

import numpy as np
import pandas as pd
import pytest

from data_generator.generate_batch import (
    LINE_COLUMNS,
    ORDER_COLUMNS,
    BatchState,
    build_batch,
    write_batch,
)


@pytest.fixture
def state() -> BatchState:
    rng = np.random.default_rng(0)
    users = pd.Series(
        rng.integers(1, 20, size=300),
        index=pd.Index(np.arange(1, 301), name="user_id"),
    )
    return BatchState(
        next_order_id=1000,
        user_last_order_number=users,
        product_ids=np.arange(1, 501, dtype=np.int64),
        product_weights=rng.integers(1, 1000, size=500).astype(float),
        last_order_date=None,
    )


def make(state, n=100, seed=1, sim_date=date(2026, 1, 1)):
    return build_batch(state, n, sim_date, "20260101", np.random.default_rng(seed))


def test_columns_and_order_count(state):
    orders, lines = make(state)
    assert list(orders.columns) == ORDER_COLUMNS
    assert list(lines.columns) == LINE_COLUMNS
    assert len(orders) == 100


def test_order_ids_continue_without_gaps_or_duplicates(state):
    orders, _ = make(state)
    assert orders.order_id.is_unique
    assert orders.order_id.min() == 1000
    assert orders.order_id.max() == 1099


def test_one_order_per_customer_and_next_order_number(state):
    orders, _ = make(state)
    assert orders.user_id.is_unique
    expected = state.user_last_order_number.loc[orders.user_id].to_numpy() + 1
    assert (orders.order_number.to_numpy() == expected).all()


def test_lines_belong_to_orders_and_have_no_repeated_products(state):
    orders, lines = make(state)
    assert set(lines.order_id) <= set(orders.order_id)
    assert not lines.duplicated(["order_id", "product_id"]).any()
    assert set(lines.product_id) <= set(state.product_ids)


def test_add_to_cart_order_is_contiguous_from_one(state):
    _, lines = make(state)
    per_order = lines.groupby("order_id")["add_to_cart_order"]
    assert (per_order.min() == 1).all()
    assert (per_order.max() == per_order.count()).all()


def test_value_ranges(state):
    orders, lines = make(state)
    assert orders.order_hour_of_day.between(0, 23).all()
    assert orders.order_dow.between(0, 6).all()
    assert orders.days_since_prior_order.between(1, 30).all()
    assert set(lines.reordered.unique()) <= {0, 1}


def test_same_seed_is_reproducible(state):
    a_orders, a_lines = make(state, seed=7)
    b_orders, b_lines = make(state, seed=7)
    pd.testing.assert_frame_equal(a_orders, b_orders)
    pd.testing.assert_frame_equal(a_lines, b_lines)


def test_too_many_orders_raises(state):
    with pytest.raises(ValueError):
        make(state, n=301)


def test_write_batch_creates_csvs(state, tmp_path):
    orders, lines = make(state)
    o_path, l_path = write_batch(orders, lines, tmp_path, "20260101")
    assert o_path.exists() and l_path.exists()
    assert len(pd.read_csv(o_path)) == len(orders)
    assert len(pd.read_csv(l_path)) == len(lines)
