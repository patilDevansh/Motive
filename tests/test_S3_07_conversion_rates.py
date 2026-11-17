import pytest
from fastapi.testclient import TestClient

from api.store import create_app
from src.event_store import EventStore
from src.product_event_stats import get_product_stats

CATALOG = (
    "product_id,name,category,price,currency,available,url\n"
    "p1,Blue Mug,kitchen,10,USD,true,\n"
    "p2,Red Lamp,home,25,USD,true,\n"
    "p3,Green Pen,office,2,USD,true,\n"
    "p4,Gray Sock,clothes,5,USD,true,\n"
    "p5,Pink Cup,kitchen,8,USD,true,\n"
)

EVENTS = (
    "event_id,shopper_id,product_id,event,timestamp\n"
    "e1,u1,p1,view,2026-10-01T10:00:00Z\n"
    "e2,u2,p1,view,2026-10-02T10:00:00Z\n"
    "e3,u2,p1,cart,2026-10-02T10:05:00Z\n"
    "e4,u3,p1,view,2026-10-03T10:00:00Z\n"
    "e5,u3,p1,purchase,2026-10-03T10:10:00Z\n"
    "e6,u1,p2,view,2026-10-04T10:00:00Z\n"
    "e7,u2,p2,view,2026-10-04T11:00:00Z\n"
    "e8,u3,p2,view,2026-10-04T12:00:00Z\n"
    "e9,u4,p2,view,2026-10-04T13:00:00Z\n"
    "e10,u1,p2,cart,2026-10-04T10:05:00Z\n"
    "e11,u2,p2,cart,2026-10-04T11:05:00Z\n"
    "e12,u1,p2,purchase,2026-10-04T10:10:00Z\n"
    "e13,u5,p4,cart,2026-10-05T10:00:00Z\n"
    "e14,u6,p5,view,2026-10-06T10:00:00Z\n"
    "e15,u6,p5,cart,2026-10-06T10:01:00Z\n"
    "e16,u7,p5,cart,2026-10-06T11:00:00Z\n"
)


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "store.sqlite3")
    store = EventStore(path)
    store.import_catalog("store-a", CATALOG)
    store.import_events("store-a", EVENTS)
    return path


def by_id(result):
    #turn the items list into a dict so its easy to look up a product
    products = {}
    for item in result["items"]:
        products[item["product_id"]] = item
    return products


def test_S3_07_rates_match_counts(db_path):
    products = by_id(get_product_stats(db_path, "store-a"))

    #1 cart and 1 purchase out of 3 views, rounded to 4 places
    assert products["p1"]["view_to_cart_rate"] == 0.3333
    assert products["p1"]["view_to_purchase_rate"] == 0.3333

    #2 carts and 1 purchase out of 4 views
    assert products["p2"]["view_to_cart_rate"] == 0.5
    assert products["p2"]["view_to_purchase_rate"] == 0.25


def test_S3_07_no_views_gives_null(db_path):
    products = by_id(get_product_stats(db_path, "store-a"))

    #p3 has no events and p4 has a cart but no views
    for product_id in ["p3", "p4"]:
        assert products[product_id]["view_to_cart_rate"] is None
        assert products[product_id]["view_to_purchase_rate"] is None


def test_S3_07_rate_not_capped(db_path):
    products = by_id(get_product_stats(db_path, "store-a"))

    #1 view but 2 carts so the rate is over 1
    assert products["p5"]["view_to_cart_rate"] == 2.0
    assert products["p5"]["view_to_purchase_rate"] == 0.0


def test_S3_07_rates_follow_date_range(db_path):
    result = get_product_stats(db_path, "store-a", start="2026-10-01T00:00:00Z", end="2026-10-03T00:00:00Z")
    p1 = by_id(result)["p1"]

    #the 10-03 view and purchase are outside the window
    assert p1["views"] == 2
    assert p1["carts"] == 1
    assert p1["purchases"] == 0
    assert p1["view_to_cart_rate"] == 0.5
    assert p1["view_to_purchase_rate"] == 0.0


def test_S3_07_api_returns_rates(db_path):
    client = TestClient(create_app(db_path))
    response = client.get("/stores/store-a/products/stats")

    assert response.status_code == 200
    items = response.json()["items"]
    for item in items:
        assert "view_to_cart_rate" in item
        assert "view_to_purchase_rate" in item

    products = by_id(response.json())
    assert products["p3"]["view_to_cart_rate"] is None
    assert products["p3"]["view_to_purchase_rate"] is None
