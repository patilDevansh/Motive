from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import pickle

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

events = pd.read_csv(
    DATA_DIR / "events.csv"
)

events = events.drop_duplicates().copy()

events["datetime"] = pd.to_datetime(
    events["timestamp"],
    unit="ms"
)


history = events[
    events["datetime"] < "2015-08-01"
].copy()


print(
    "History rows:",
    history.shape
)

history = history.sort_values(
    [
        "visitorid",
        "datetime"
    ]
).copy()


history["previous_time"] = (
    history
    .groupby("visitorid")[
        "datetime"
    ]
    .shift(1)
)


history["gap_minutes"] = (
    (
        history["datetime"]
        - history["previous_time"]
    )
    .dt.total_seconds()
    / 60
)


history["new_session"] = (
    history["previous_time"].isna()
    |
    (history["gap_minutes"] > 30)
)


history["session_number"] = (
    history
    .groupby("visitorid")[
        "new_session"
    ]
    .cumsum()
)


history["session_id"] = (
    history["visitorid"].astype(str)
    + "_"
    + history[
        "session_number"
    ].astype(str)
)


print(
    "Sessions:",
    history[
        "session_id"
    ].nunique()
)

session_items = (
    history[
        [
            "session_id",
            "itemid"
        ]
    ]
    .drop_duplicates()
)


session_sizes = (
    session_items
    .groupby("session_id")
    ["itemid"]
    .nunique()
)


print(
    "\nSession size summary:"
)

print(
    session_sizes.describe()
)

valid_sessions = session_sizes[
    (session_sizes >= 2)
    &
    (session_sizes <= 20)
].index


session_items = session_items[
    session_items[
        "session_id"
    ].isin(valid_sessions)
]


print(
    "\nValid multi-item sessions:",
    len(valid_sessions)
)

pair_counts = Counter()


grouped_sessions = (
    session_items
    .groupby("session_id")[
        "itemid"
    ]
    .apply(list)
)


for i, items in enumerate(
    grouped_sessions
):

    items = [
        int(item)
        for item in items
    ]

    for item_a, item_b in combinations(
        items,
        2
    ):
        if item_a == item_b:
            continue

        pair_counts[
            (
                item_a,
                item_b
            )
        ] += 1

        pair_counts[
            (
                item_b,
                item_a
            )
        ] += 1

    if (i + 1) % 100000 == 0:
        print(
            f"Processed "
            f"{i + 1:,} sessions"
        )


print(
    "\nDirected item pairs:",
    len(pair_counts)
)

neighbors = defaultdict(list)


for (
    source_item,
    target_item
), score in pair_counts.items():

    neighbors[
        source_item
    ].append(
        (
            target_item,
            float(score)
        )
    )

TOP_K = 100


covisitation_neighbor_map = {}


for item_id, item_neighbors in (
    neighbors.items()
):

    item_neighbors.sort(
        key=lambda x: x[1],
        reverse=True
    )

    covisitation_neighbor_map[
        int(item_id)
    ] = item_neighbors[:TOP_K]

output_path = (
    ARTIFACT_DIR
    / "reranker_covisitation.pkl"
)


with open(
    output_path,
    "wb"
) as f:

    pickle.dump(
        covisitation_neighbor_map,
        f
    )


print(
    "\nItems with co-visitation neighbors:",
    len(
        covisitation_neighbor_map
    )
)

print(
    "Saved to:",
    output_path
)