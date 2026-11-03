import numpy as np
import pandas as pd


class ContentRecommender:
    def __init__(
        self,
        normalized_item_matrix,
        item_ids,
        item_to_index,
        content_neighbors
    ):
        self.normalized_item_matrix = normalized_item_matrix
        self.item_ids = item_ids
        self.item_to_index = item_to_index
        self.content_neighbors = content_neighbors

    def get_similar_items(self, item_id, k=20):
        item_id = int(item_id)
        cache_key = (item_id, k)

        # 1. Fast path: use precomputed/cached neighbors
        if cache_key in self.content_neighbors:
            return self.content_neighbors[cache_key].copy()

        # 2. If item is unknown to content model
        target_index = self.item_to_index.get(item_id)

        if target_index is None:
            return pd.DataFrame(
                columns=["itemid", "similarity"]
            )

        # 3. Compute similarity only when cache is missing
        similarities = (
            self.normalized_item_matrix[target_index]
            @ self.normalized_item_matrix.T
        ).toarray().ravel()

        # Don't recommend the item itself
        similarities[target_index] = -1

        if k < len(similarities):
            top_indices = np.argpartition(
                similarities,
                -k
            )[-k:]

            top_indices = top_indices[
                np.argsort(
                    similarities[top_indices]
                )[::-1]
            ]
        else:
            top_indices = np.argsort(
                similarities
            )[::-1]

        recommendations = pd.DataFrame({
            "itemid": self.item_ids[top_indices],
            "similarity": similarities[top_indices]
        }).reset_index(drop=True)

        # 4. Cache new result in memory
        self.content_neighbors[cache_key] = recommendations

        return recommendations.copy()