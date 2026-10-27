from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.product_stats import build_product_stats, save_product_stats


EVENTS_PATH = PROJECT_ROOT / "data" / "events.csv"
STATS_PATH = PROJECT_ROOT / "artifacts" / "product_stats.pkl"


def main():
    events = pd.read_csv(EVENTS_PATH)
    print("Loaded events:", events.shape)

    stats = build_product_stats(events)
    print("Products with stats:", len(stats))

    STATS_PATH.parent.mkdir(exist_ok=True)
    save_product_stats(stats, STATS_PATH)
    print("Saved to", STATS_PATH)

    print(stats.head(10))


if __name__ == "__main__":
    main()
