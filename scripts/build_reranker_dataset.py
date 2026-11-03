from pathlib import Path
import pickle

import pandas as pd

from src.artifacts import load_artifacts
from src.content import ContentRecommender
from src.popularity import PopularityRecommender
from src.routing import UserRouter
from src.candidates import CandidateGenerator
from src.features import FeatureBuilder
from src.covisitation import CovisitationRecommender


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

COVISITATION_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_covisitation.pkl"
)

with open(
    COVISITATION_PATH,
    "rb"
) as f:
    covisitation_neighbor_map = pickle.load(f)

covisitation_model = CovisitationRecommender(
    neighbor_map=covisitation_neighbor_map
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


# --------------------------------------------------
# Load behavioral data
# --------------------------------------------------

events = pd.read_csv(
    DATA_DIR / "events.csv"
)

events = events.drop_duplicates().copy()

events["datetime"] = pd.to_datetime(
    events["timestamp"],
    unit="ms"
)


# --------------------------------------------------
# Chronological split for reranker training
# --------------------------------------------------

history_data = events[
    events["datetime"] < "2015-08-01"
].copy()

label_data = events[
    (events["datetime"] >= "2015-08-01")
    & (events["datetime"] < "2015-09-01")
].copy()


print("History:", history_data.shape)
print("August labels:", label_data.shape)
print()

print(
    "History users:",
    history_data["visitorid"].nunique()
)

print(
    "August users:",
    label_data["visitorid"].nunique()
)

interaction_weights = {
    "view": 1,
    "addtocart": 3,
    "transaction": 5
}


history_cf = history_data[
    ["visitorid", "itemid", "event"]
].copy()

history_cf["weight"] = history_cf[
    "event"
].map(interaction_weights)


reranker_user_item_strength = (
    history_cf
    .groupby(
        ["visitorid", "itemid"]
    )["weight"]
    .sum()
    .reset_index()
)


reranker_user_history_count = (
    reranker_user_item_strength
    .groupby("visitorid")["itemid"]
    .nunique()
)


print(
    "\nUser-item strength:",
    reranker_user_item_strength.shape
)

print(
    "Users with history:",
    len(reranker_user_history_count)
)

history_weighted = history_data[
    ["itemid", "event"]
].copy()

history_weighted["weight"] = (
    history_weighted["event"]
    .map(interaction_weights)
)


reranker_weighted_popularity = (
    history_weighted
    .groupby("itemid")["weight"]
    .sum()
    .sort_values(ascending=False)
)


print(
    "\nPopularity items:",
    len(reranker_weighted_popularity)
)

history_users = set(
    reranker_user_item_strength[
        "visitorid"
    ].unique()
)

august_users = set(
    label_data[
        "visitorid"
    ].unique()
)

reranker_users = (
    history_users
    & august_users
)


print(
    "\nUsers with history AND August activity:",
    len(reranker_users)
)
history_users = set(
    reranker_user_item_strength[
        "visitorid"
    ].unique()
)

august_users = set(
    label_data[
        "visitorid"
    ].unique()
)

reranker_users = (
    history_users
    & august_users
)


# --------------------------------------------------
# Analyze eligible reranker users
# --------------------------------------------------

eligible_users_df = pd.DataFrame({
    "visitorid": list(reranker_users)
})

eligible_users_df["history_count"] = (
    eligible_users_df["visitorid"]
    .map(reranker_user_history_count)
    .fillna(0)
    .astype(int)
)

eligible_users_df["segment"] = pd.cut(
    eligible_users_df["history_count"],
    bins=[-1, 0, 2, float("inf")],
    labels=[
        "new_user",
        "low_history",
        "established"
    ]
)

print("\nEligible user segments:")
print(
    eligible_users_df["segment"]
    .value_counts()
)

# --------------------------------------------------
# Prototype reranker training sample
# --------------------------------------------------

low_history_users = eligible_users_df[
    eligible_users_df["segment"] == "low_history"
]

established_users = eligible_users_df[
    eligible_users_df["segment"] == "established"
]

low_sample = low_history_users.sample(
    n=min(1000, len(low_history_users)),
    random_state=42
)

established_sample = established_users.sample(
    n=min(1000, len(established_users)),
    random_state=42
)

training_users_sample = pd.concat(
    [
        low_sample,
        established_sample
    ],
    ignore_index=True
)

print(
    "\nPrototype users:",
    len(training_users_sample)
)

print(
    training_users_sample["segment"]
    .value_counts()
)

# --------------------------------------------------
# Build reranker candidate-generation environment
# --------------------------------------------------

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

reranker_popularity_model = PopularityRecommender(
    weighted_popularity=
        reranker_weighted_popularity
)

reranker_router = UserRouter(
    user_history_count=
        reranker_user_history_count
)

candidate_generator = CandidateGenerator(
    content_model=content_model,
    popularity_model=reranker_popularity_model,
    router=reranker_router,
    user_item_strength=reranker_user_item_strength,
    covisitation_model=covisitation_model
)

feature_builder = FeatureBuilder()

# --------------------------------------------------
# Build August ground-truth lookup
# --------------------------------------------------

august_actual_items = (
    label_data
    .groupby("visitorid")["itemid"]
    .apply(
        lambda x: set(
            x.astype(int)
        )
    )
    .to_dict()
)

# --------------------------------------------------
# Generate labeled candidate rows
# --------------------------------------------------

training_rows = []

users_with_candidate_hit = 0

for i, row in training_users_sample.iterrows():

    user_id = int(row["visitorid"])

    candidates = candidate_generator.generate(
        user_id=user_id,
        n_candidates=200,
        neighbors_per_item=50,
        max_history_items=20,
        popularity_candidates=0,
        covisitation_neighbors_per_item=50
    )
    candidates = feature_builder.build(
        candidates
    )

    actual_items = august_actual_items.get(
        user_id,
        set()
    )

    candidates["label"] = (
        candidates["itemid"]
        .astype(int)
        .isin(actual_items)
        .astype(int)
    )

    candidates["visitorid"] = user_id

    if candidates["label"].sum() > 0:
        users_with_candidate_hit += 1

    training_rows.append(candidates)

    if (i + 1) % 25 == 0:
        print(
            f"Processed {i + 1}/"
            f"{len(training_users_sample)} users"
        )

reranker_training_df = pd.concat(
    training_rows,
    ignore_index=True
)

user_candidate_stats = []

for _, row in training_users_sample.iterrows():
    user_id = int(row["visitorid"])
    segment = str(row["segment"])

    user_rows = reranker_training_df[
        reranker_training_df["visitorid"] == user_id
    ]

    positives = int(
        user_rows["label"].sum()
    )

    user_candidate_stats.append({
        "visitorid": user_id,
        "segment": segment,
        "candidate_count": len(user_rows),
        "positive_candidates": positives,
        "has_hit": int(positives > 0)
    })


user_candidate_stats_df = pd.DataFrame(
    user_candidate_stats
)


segment_candidate_summary = (
    user_candidate_stats_df
    .groupby("segment")
    .agg(
        users=("visitorid", "count"),
        users_with_hit=("has_hit", "sum"),
        hit_rate=("has_hit", "mean"),
        avg_candidates=("candidate_count", "mean"),
        positive_candidates=(
            "positive_candidates",
            "sum"
        )
    )
)


print(
    "\n--- CURRENT CANDIDATE RECALL BY SEGMENT ---"
)

print(segment_candidate_summary)

print(
    "\nTraining rows:",
    reranker_training_df.shape
)

print(
    "\nLabel distribution:"
)

print(
    reranker_training_df[
        "label"
    ].value_counts()
)

print(
    "\nPositive labels:",
    reranker_training_df[
        "label"
    ].sum()
)

print(
    "Users with >=1 positive candidate:",
    users_with_candidate_hit
)

print(
    "Candidate hit rate:",
    users_with_candidate_hit
    / len(training_users_sample)
)

user_candidate_stats = []

for _, row in training_users_sample.iterrows():
    user_id = int(row["visitorid"])
    segment = str(row["segment"])

    user_rows = reranker_training_df[
        reranker_training_df["visitorid"] == user_id
    ]

    user_candidate_stats.append({
        "visitorid": user_id,
        "segment": segment,
        "candidate_count": len(user_rows),
        "positive_candidates": int(
            user_rows["label"].sum()
        ),
        "has_hit": int(
            user_rows["label"].sum() > 0
        )
    })

user_candidate_stats_df = pd.DataFrame(
    user_candidate_stats
)

print(
    user_candidate_stats_df
    .groupby("segment")
    .agg(
        users=("visitorid", "count"),
        users_with_hit=("has_hit", "sum"),
        hit_rate=("has_hit", "mean"),
        avg_candidates=("candidate_count", "mean"),
        positive_candidates=("positive_candidates", "sum")
    )
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_training_data.pkl"
)

reranker_training_df.to_pickle(
    OUTPUT_PATH
)

print(
    "\nSaved reranker training dataset to:",
    OUTPUT_PATH
)