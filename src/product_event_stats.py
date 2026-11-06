import sqlite3
from datetime import datetime, timezone

from src.catalog_store import ImportValidationError, error, store_key

#counts views, carts and purchases for every product in one store
#LEFT JOIN so products with no events still show up (with 0)
#join on store_id too so other stores events dont get counted
#the date checks are in the JOIN (not WHERE) so products with no events in the window still show up
#if start or end is None that check is skipped
#julianday turns the timestamp text into a number so 00:00:00.001Z vs 00:00:00Z compares right
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
    AND (? IS NULL OR julianday(e.timestamp) >= julianday(?))
    AND (? IS NULL OR julianday(e.timestamp) < julianday(?))
WHERE p.store_id = ?
GROUP BY p.product_id
ORDER BY p.product_id
LIMIT ? OFFSET ?
"""


def parse_time(text, field):
    if text is None:
        return None

    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ImportValidationError([error(0, field, "Expected ISO 8601 timestamp")])

    if value.tzinfo is None:
        raise ImportValidationError([error(0, field, "Expected ISO 8601 with timezone")])

    #change to UTC because thats how S2-04 stores event times
    return value.astimezone(timezone.utc)


def get_product_stats(db_path, store_id, limit=50, offset=0, start=None, end=None):
    store_id = store_key(store_id)

    start_time = parse_time(start, "start")
    end_time = parse_time(end, "end")

    if start_time is not None and end_time is not None and start_time >= end_time:
        raise ImportValidationError([error(0, "start", "start must be before end")])

    #turn them back into text for the query (None stays None)
    start_text = None
    if start_time is not None:
        start_text = start_time.isoformat()

    end_text = None
    if end_time is not None:
        end_text = end_time.isoformat()

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        total = db.execute(
            "SELECT COUNT(*) FROM products WHERE store_id = ?",
            (store_id,)
        ).fetchone()[0]

        rows = db.execute(
            STATS_QUERY,
            (start_text, start_text, end_text, end_text, store_id, limit, offset)
        ).fetchall()
    finally:
        db.close()

    items = []
    for row in rows:
        items.append(dict(row))

    return {"items": items, "total": total, "limit": limit, "offset": offset}
