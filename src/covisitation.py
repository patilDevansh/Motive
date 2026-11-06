import pandas as pd


class CovisitationRecommender:

    def __init__(self, neighbor_map):
        """
        neighbor_map format:

        {
            item_id: [
                (neighbor_item_id, score),
                ...
            ]
        }
        """
        self.neighbor_map = neighbor_map


    def get_related_items(
        self,
        item_id,
        k=50
    ):
        item_id = int(item_id)

        neighbors = self.neighbor_map.get(
            item_id,
            []
        )

        neighbors = neighbors[:k]

        if not neighbors:
            return pd.DataFrame(
                columns=[
                    "itemid",
                    "covisitation_score"
                ]
            )

        return pd.DataFrame(
            neighbors,
            columns=[
                "itemid",
                "covisitation_score"
            ]
        )