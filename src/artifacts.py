from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import load_npz


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"


def load_artifacts():
    artifacts = {}

    artifacts["normalized_item_matrix"] = load_npz(
        ARTIFACT_DIR / "normalized_item_matrix.npz"
    )

    artifacts["item_ids"] = np.load(
        ARTIFACT_DIR / "item_ids.npy"
    )

    with open(
        ARTIFACT_DIR / "item_to_index.pkl",
        "rb"
    ) as f:
        artifacts["item_to_index"] = pickle.load(f)

    with open(
        ARTIFACT_DIR / "weighted_popularity.pkl",
        "rb"
    ) as f:
        artifacts["weighted_popularity"] = pickle.load(f)

    with open(
        ARTIFACT_DIR / "user_history_count.pkl",
        "rb"
    ) as f:
        artifacts["user_history_count"] = pickle.load(f)

    with open(
        ARTIFACT_DIR / "content_neighbors.pkl",
        "rb"
    ) as f:
        artifacts["content_neighbors"] = pickle.load(f)

    artifacts["user_item_strength"] = pd.read_pickle(
        ARTIFACT_DIR / "user_item_strength.pkl"
    )

    return artifacts