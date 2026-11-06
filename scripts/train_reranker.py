from pathlib import Path
import pickle

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import HistGradientBoostingClassifier



PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_training_data.pkl"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_logistic.pkl"
)


# --------------------------------------------------
# Load candidate training dataset
# --------------------------------------------------

df = pd.read_pickle(
    DATA_PATH
)

print(
    "Dataset:",
    df.shape
)

print(
    "\nLabels:"
)

print(
    df["label"]
    .value_counts()
)


# --------------------------------------------------
# Add simple segment feature
# --------------------------------------------------

df["is_established"] = (
    df["segment"] == "established"
).astype(int)


# --------------------------------------------------
# Features used by learned reranker
# --------------------------------------------------

FEATURE_COLUMNS = [
    "content_score",
    "max_content_similarity",
    "history_support_count",

    "covisitation_score",
    "max_covisitation_score",
    "covisitation_support_count",

    "popularity_score",
    "user_history_count",

    "log_popularity",
    "multi_history_support",
    "avg_content_support",

    "log_covisitation_score",
    "multi_covisitation_support",
    "avg_covisitation_support",

    "is_established"

]

missing_features = [
    column
    for column in FEATURE_COLUMNS
    if column not in df.columns
]

if missing_features:
    raise ValueError(
        "Missing reranker features: "
        f"{missing_features}"
    )

# --------------------------------------------------
# Build user-level split table
# --------------------------------------------------

user_summary = (
    df
    .groupby("visitorid")
    .agg(
        segment=("segment", "first"),
        has_positive=(
            "label",
            lambda x: int(x.sum() > 0)
        )
    )
    .reset_index()
)


user_summary["stratify_group"] = (
    user_summary["segment"].astype(str)
    + "_"
    + user_summary[
        "has_positive"
    ].astype(str)
)


train_users, validation_users = (
    train_test_split(
        user_summary,
        test_size=0.20,
        random_state=42,
        stratify=user_summary[
            "stratify_group"
        ]
    )
)


train_user_ids = set(
    train_users["visitorid"]
)

validation_user_ids = set(
    validation_users["visitorid"]
)


train_df = df[
    df["visitorid"].isin(
        train_user_ids
    )
].copy()


validation_df = df[
    df["visitorid"].isin(
        validation_user_ids
    )
].copy()


print(
    "\nTrain users:",
    len(train_user_ids)
)

print(
    "Validation users:",
    len(validation_user_ids)
)

print(
    "Train rows:",
    len(train_df)
)

print(
    "Validation rows:",
    len(validation_df)
)

print(
    "Train positives:",
    int(train_df["label"].sum())
)

print(
    "Validation positives:",
    int(validation_df["label"].sum())
)

X_train = train_df[
    FEATURE_COLUMNS
].astype(float)

y_train = train_df[
    "label"
].astype(int)


model = Pipeline(
    [
        (
            "scaler",
            StandardScaler()
        ),
        (
            "model",
            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42
            )
        )
    ]
)


print(
    "\nTraining logistic reranker..."
)

model.fit(
    X_train,
    y_train
)

print(
    "Training complete."
)

X_validation = validation_df[
    FEATURE_COLUMNS
].astype(float)


validation_df[
    "reranker_score"
] = model.predict_proba(
    X_validation
)[:, 1]


# --------------------------------------------------
# Train nonlinear tree-based reranker
# --------------------------------------------------

tree_model = HistGradientBoostingClassifier(
    learning_rate=0.08,
    max_iter=200,
    max_leaf_nodes=31,
    min_samples_leaf=20,
    l2_regularization=1.0,
    random_state=42
)

print(
    "\nTraining nonlinear tree reranker..."
)

tree_model.fit(
    X_train,
    y_train
)

print(
    "Tree training complete."
)

validation_df[
    "tree_reranker_score"
] = tree_model.predict_proba(
    X_validation
)[:, 1]

tree_auc = roc_auc_score(
    validation_df["label"],
    validation_df[
        "tree_reranker_score"
    ]
)

print(
    "\nTree validation ROC-AUC:",
    round(tree_auc, 4)
)

auc = roc_auc_score(
    validation_df["label"],
    validation_df[
        "reranker_score"
    ]
)

print(
    "\nValidation ROC-AUC:",
    round(auc, 4)
)


def evaluate_ranking(
    data,
    score_column,
    k=10
):
    precisions = []
    recalls = []
    hit_rates = []
    reciprocal_ranks = []
    ndcgs = []

    for _, user_rows in data.groupby(
        "visitorid"
    ):

        ranked = (
            user_rows
            .sort_values(
                score_column,
                ascending=False
            )
            .head(k)
        )

        relevant_total = int(
            user_rows["label"].sum()
        )

        if relevant_total == 0:
            continue

        labels = (
            ranked["label"]
            .astype(int)
            .to_numpy()
        )

        hits = int(
            labels.sum()
        )

        precisions.append(
            hits / k
        )

        recalls.append(
            hits / relevant_total
        )

        hit_rates.append(
            int(hits > 0)
        )

        # -----------------------------
        # Reciprocal Rank
        # -----------------------------

        positive_positions = np.where(
            labels == 1
        )[0]

        if len(positive_positions) > 0:
            reciprocal_rank = (
                1.0
                / (
                    positive_positions[0]
                    + 1
                )
            )
        else:
            reciprocal_rank = 0.0

        reciprocal_ranks.append(
            reciprocal_rank
        )

        # -----------------------------
        # NDCG@K
        # -----------------------------

        discounts = (
            1.0
            / np.log2(
                np.arange(
                    2,
                    len(labels) + 2
                )
            )
        )

        dcg = float(
            np.sum(
                labels
                * discounts
            )
        )

        ideal_hits = min(
            relevant_total,
            k
        )

        ideal_labels = np.ones(
            ideal_hits
        )

        ideal_discounts = (
            1.0
            / np.log2(
                np.arange(
                    2,
                    ideal_hits + 2
                )
            )
        )

        idcg = float(
            np.sum(
                ideal_labels
                * ideal_discounts
            )
        )

        ndcg = (
            dcg / idcg
            if idcg > 0
            else 0.0
        )

        ndcgs.append(
            ndcg
        )

    return {
        "precision@10":
            np.mean(precisions),

        "recall@10":
            np.mean(recalls),

        "hit_rate@10":
            np.mean(hit_rates),

        "mrr":
            np.mean(
                reciprocal_ranks
            ),

        "ndcg@10":
            np.mean(ndcgs),

        "evaluated_users":
            len(hit_rates)
    }

validation_df[
    "_content_norm"
] = validation_df.groupby(
    "visitorid"
)["content_score"].transform(
    lambda x: (
        x / x.max()
        if x.max() > 0
        else 0.0
    )
)


validation_df[
    "_covis_norm"
] = validation_df.groupby(
    "visitorid"
)["covisitation_score"].transform(
    lambda x: (
        x / x.max()
        if x.max() > 0
        else 0.0
    )
)


validation_df[
    "baseline_score"
] = (
    validation_df[
        "_content_norm"
    ]
    +
    validation_df[
        "_covis_norm"
    ]
)

baseline_metrics = evaluate_ranking(
    validation_df,
    score_column="baseline_score",
    k=10
)


reranker_metrics = evaluate_ranking(
    validation_df,
    score_column="reranker_score",
    k=10
)


tree_metrics = evaluate_ranking(
    validation_df,
    score_column="tree_reranker_score",
    k=10
)

print(
    "\n--- BASELINE RANKING ---"
)

for metric, value in (
    baseline_metrics.items()
):
    print(
        metric,
        round(value, 6)
        if isinstance(
            value,
            float
        )
        else value
    )


print(
    "\n--- LEARNED RERANKER ---"
)

print(
    "\n--- TREE RERANKER ---"
)

for metric, value in tree_metrics.items():
    print(
        metric,
        round(value, 6)
        if isinstance(value, float)
        else value
    )

for metric, value in (
    reranker_metrics.items()
):
    print(
        metric,
        round(value, 6)
        if isinstance(
            value,
            float
        )
        else value
    )

model_artifact = {
    "model": model,
    "feature_columns":
        FEATURE_COLUMNS
}


with open(
    MODEL_PATH,
    "wb"
) as f:
    pickle.dump(
        model_artifact,
        f
    )


print(
    "\nSaved reranker model to:",
    MODEL_PATH
)
TREE_MODEL_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "reranker_tree.pkl"
)

tree_model_artifact = {
    "model": tree_model,
    "feature_columns": FEATURE_COLUMNS
}

with open(
    TREE_MODEL_PATH,
    "wb"
) as f:
    pickle.dump(
        tree_model_artifact,
        f
    )

print(
    "\nSaved tree reranker model to:",
    TREE_MODEL_PATH
)
