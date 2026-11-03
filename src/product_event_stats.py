import sqlite3

from src.catalog_store import store_key

#counts views, carts and purchases for every product in one store
#LEFT JOIN so products with no events still show up (with 0)
#join on store_id too so other stores events dont get counted
STATS_QUERY = """
SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(CASE WHEN e.event = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN e.event = 'cart' THEN 1 ELSE 0 END) AS carts,
    SUM(CASE WHEN e.event = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM products p
LEFT JOIN events e
    ON e.store_id = p.store_id
    AND e.product_id = p.product_id
WHERE p.store_id = ?
GROUP BY p.product_id
ORDER BY p.product_id
LIMIT ? OFFSET ?
"""


def get_product_stats(db_path, store_id, limit=50, offset=0):
    store_id = store_key(store_id)

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        total = db.execute(
            "SELECT COUNT(*) FROM products WHERE store_id = ?",
            (store_id,)
        ).fetchone()[0]

        rows = db.execute(STATS_QUERY, (store_id, limit, offset)).fetchall()
    finally:
        db.close()

    items = []
    for row in rows:
        items.append(dict(row))

    return {"items": items, "total": total, "limit": limit, "offset": offset}
