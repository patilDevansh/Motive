from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.product_stats import ProductStats, load_product_stats


STATS_PATH = PROJECT_ROOT / "artifacts" / "product_stats.pkl"
PAGE_PATH = PROJECT_ROOT / "reports" / "product_stats.html"

# change these to show more products or sort by something else
TOP_N = 100
SORT_BY = "purchases"


def build_page(table):
    table = table.copy()
    table["view_to_cart_rate"] = table["view_to_cart_rate"].map("{:.1%}".format)
    table["cart_to_purchase_rate"] = table["cart_to_purchase_rate"].map("{:.1%}".format)

    table_html = table.to_html(index=False, border=0)

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Motive Product Stats</title>
<style>
  body {{ font-family: sans-serif; margin: 24px; }}
  table {{ border-collapse: collapse; }}
  th, td {{ padding: 6px 12px; border-bottom: 1px solid #ddd; text-align: right; }}
  th {{ background: #f2f2f2; }}
</style>
</head>
<body>
<h1>Product Stats</h1>
<p>Top {TOP_N} products by {SORT_BY}.</p>
{table_html}
</body>
</html>
"""


def main():
    product_stats = ProductStats(load_product_stats(STATS_PATH))
    table = product_stats.top_n(n=TOP_N, by=SORT_BY)

    PAGE_PATH.parent.mkdir(exist_ok=True)
    PAGE_PATH.write_text(build_page(table), encoding="utf-8")
    print("Wrote", PAGE_PATH)


if __name__ == "__main__":
    main()
