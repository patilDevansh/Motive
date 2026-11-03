import pandas as pd


class PopularityRecommender:
    def __init__(self, weighted_popularity):
        self.weighted_popularity = weighted_popularity

    def recommend(self, k=10):
        top_items = (
            self.weighted_popularity
            .head(k)
        )

        return pd.DataFrame({
            "itemid": top_items.index.astype(int),
            "score": top_items.values.astype(float),
            "source": "weighted_popularity_cold_start"
        }).reset_index(drop=True)