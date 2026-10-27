from pathlib import Path

import pandas as pd

from src.product_stats import (
    ProductStats,
    build_product_stats,
    load_product_stats,
    save_product_stats,
)


SAMPLE_PATH = Path(__file__).parent / "fixtures" / "sample_events.csv"


def load_sample():
    return pd.read_csv(SAMPLE_PATH)


def test_counts_match_raw_events():
    events = load_sample().drop_duplicates()
    stats = build_product_stats(load_sample())

    # count each product by hand from the raw rows and compare
    for item_id in events["itemid"].unique():
        item_events = events[events["itemid"] == item_id]

        assert stats.loc[item_id, "views"] == (item_events["event"] == "view").sum()
        assert stats.loc[item_id, "add_to_carts"] == (item_events["event"] == "addtocart").sum()
        assert stats.loc[item_id, "purchases"] == (item_events["event"] == "transaction").sum()


def test_every_product_is_included():
    events = load_sample()
    stats = build_product_stats(events)

    assert set(stats.index) == set(events["itemid"].unique())


def test_duplicate_rows_are_dropped():
    stats = build_product_stats(load_sample())

    # item 100 has the same addtocart row twice in the sample
    assert stats.loc[100, "add_to_carts"] == 1


def test_rates():
    stats = build_product_stats(load_sample())

    # item 100: 4 views, 1 cart, 1 purchase
    assert stats.loc[100, "view_to_cart_rate"] == 0.25
    assert stats.loc[100, "cart_to_purchase_rate"] == 1.0

    # item 200: 2 views, 1 cart, 0 purchases
    assert stats.loc[200, "view_to_cart_rate"] == 0.5
    assert stats.loc[200, "cart_to_purchase_rate"] == 0.0


def test_rates_are_zero_when_nothing_to_divide_by():
    stats = build_product_stats(load_sample())

    # item 400 was bought with no view or cart event
    assert stats.loc[400, "view_to_cart_rate"] == 0.0
    assert stats.loc[400, "cart_to_purchase_rate"] == 0.0


def test_get_product():
    product_stats = ProductStats(build_product_stats(load_sample()))

    result = product_stats.get_product(200)

    assert result == {
        "itemid": 200,
        "views": 2,
        "add_to_carts": 1,
        "purchases": 0,
        "view_to_cart_rate": 0.5,
        "cart_to_purchase_rate": 0.0,
    }


def test_get_product_unknown_item():
    product_stats = ProductStats(build_product_stats(load_sample()))

    assert product_stats.get_product(999999) is None


def test_top_n():
    product_stats = ProductStats(build_product_stats(load_sample()))

    top = product_stats.top_n(n=2, by="views")

    assert len(top) == 2
    assert top["itemid"].tolist() == [100, 200]


def test_save_and_load(tmp_path):
    stats = build_product_stats(load_sample())
    path = tmp_path / "product_stats.pkl"

    save_product_stats(stats, path)

    pd.testing.assert_frame_equal(load_product_stats(path), stats)
