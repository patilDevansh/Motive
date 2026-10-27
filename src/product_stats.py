import pandas as pd


EVENT_COLUMNS = {
    "view": "views",
    "addtocart": "add_to_carts",
    "transaction": "purchases",
}


def build_product_stats(events):
    events = events.drop_duplicates()

    counts = (
        events
        .groupby(["itemid", "event"])
        .size()
        .unstack(fill_value=0)
    )

    # make sure all three columns exist even if an event type is missing
    for event in EVENT_COLUMNS:
        if event not in counts.columns:
            counts[event] = 0

    stats = counts[list(EVENT_COLUMNS)].rename(columns=EVENT_COLUMNS)

    # a product with 0 views (or 0 carts) gets a rate of 0
    stats["view_to_cart_rate"] = (
        stats["add_to_carts"] / stats["views"]
    ).where(stats["views"] > 0, 0.0)

    stats["cart_to_purchase_rate"] = (
        stats["purchases"] / stats["add_to_carts"]
    ).where(stats["add_to_carts"] > 0, 0.0)

    stats.columns.name = None

    return stats.sort_values(
        ["purchases", "add_to_carts", "views"],
        ascending=False
    )


def save_product_stats(stats, path):
    stats.to_pickle(path)


def load_product_stats(path):
    return pd.read_pickle(path)


class ProductStats:
    def __init__(self, stats):
        self.stats = stats

    def get_product(self, item_id):
        item_id = int(item_id)

        if item_id not in self.stats.index:
            return None

        row = self.stats.loc[item_id]

        return {
            "itemid": item_id,
            "views": int(row["views"]),
            "add_to_carts": int(row["add_to_carts"]),
            "purchases": int(row["purchases"]),
            "view_to_cart_rate": float(row["view_to_cart_rate"]),
            "cart_to_purchase_rate": float(row["cart_to_purchase_rate"]),
        }

    def top_n(self, n=10, by="purchases"):
        return (
            self.stats
            .sort_values(by, ascending=False)
            .head(n)
            .reset_index()
        )
