from pathlib import Path
import pickle

from src.covisitation import CovisitationRecommender
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_covisitation.pkl"
)


with open(
    ARTIFACT_PATH,
    "rb"
) as f:
    neighbor_map = pickle.load(f)


model = CovisitationRecommender(
    neighbor_map=neighbor_map
)


print(
    "Items with neighbors:",
    len(neighbor_map)
)


# --------------------------------------------------
# Inspect a few known items
# --------------------------------------------------

test_items = [
    460429,
    187946,
    461686,
    5411
]


for item_id in test_items:

    print(
        f"\n--- ITEM {item_id} ---"
    )

    neighbors = (
        model.get_related_items(
            item_id=item_id,
            k=10
        )
    )

    print(neighbors)

from src.artifacts import load_artifacts
from src.content import ContentRecommender


artifacts = load_artifacts()

content_model = ContentRecommender(
    normalized_item_matrix=artifacts[
        "normalized_item_matrix"
    ],
    item_ids=artifacts["item_ids"],
    item_to_index=artifacts[
        "item_to_index"
    ],
    content_neighbors=artifacts[
        "content_neighbors"
    ]
)


target_item = 460429


content_neighbors = (
    content_model
    .get_similar_items(
        target_item,
        k=50
    )
)


covis_neighbors = (
    model
    .get_related_items(
        target_item,
        k=50
    )
)


content_set = set(
    content_neighbors[
        "itemid"
    ].astype(int)
)

covis_set = set(
    covis_neighbors[
        "itemid"
    ].astype(int)
)


overlap = (
    content_set
    & covis_set
)


print(
    "\n--- CONTENT VS COVISITATION ---"
)

print(
    "Content neighbors:",
    len(content_set)
)

print(
    "Covisitation neighbors:",
    len(covis_set)
)

print(
    "Overlap:",
    len(overlap)
)

print(
    "Overlap ratio:",
    len(overlap)
    / max(
        len(
            content_set
            | covis_set
        ),
        1
    )
)

print(
    "Overlapping items:",
    overlap
)

import numpy as np


# --------------------------------------------------
# Compare content vs co-visitation across many items
# --------------------------------------------------

candidate_items = [
    int(item_id)
    for item_id in neighbor_map.keys()
    if int(item_id) in artifacts["item_to_index"]
]


rng = np.random.default_rng(42)

sample_size = min(
    100,
    len(candidate_items)
)

sample_items = rng.choice(
    candidate_items,
    size=sample_size,
    replace=False
)


overlap_results = []


for item_id in sample_items:

    content_neighbors = (
        content_model.get_similar_items(
            int(item_id),
            k=50
        )
    )

    covis_neighbors = (
        model.get_related_items(
            int(item_id),
            k=50
        )
    )


    content_set = set(
        content_neighbors[
            "itemid"
        ].astype(int)
    )

    covis_set = set(
        covis_neighbors[
            "itemid"
        ].astype(int)
    )


    if not content_set or not covis_set:
        continue


    overlap = (
        content_set
        & covis_set
    )

    union = (
        content_set
        | covis_set
    )


    overlap_results.append({
        "itemid": int(item_id),
        "content_count": len(
            content_set
        ),
        "covis_count": len(
            covis_set
        ),
        "overlap_count": len(
            overlap
        ),
        "jaccard": (
            len(overlap)
            / len(union)
        )
    })


overlap_df = pd.DataFrame(
    overlap_results
)


print(
    "\n--- CONTENT VS COVISITATION SAMPLE ---"
)

print(
    "Items compared:",
    len(overlap_df)
)


print(
    "\nOverlap count summary:"
)

print(
    overlap_df[
        "overlap_count"
    ].describe()
)


print(
    "\nJaccard overlap summary:"
)

print(
    overlap_df[
        "jaccard"
    ].describe()
)


print(
    "\nAverage overlap:",
    overlap_df[
        "overlap_count"
    ].mean()
)


print(
    "Average Jaccard:",
    overlap_df[
        "jaccard"
    ].mean()
)