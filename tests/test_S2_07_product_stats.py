import pytest
from fastapi.testclient import TestClient

from api.store import create_app
from src.event_store import EventStore
from src.product_event_stats import get_product_stats

CATALOG_A = (
    "product_id,name,category,price,currency,available,url\n"
    "p1,Blue Mug,kitchen,10,USD,true,\n"
    "p2,Red Lamp,home,25,USD,true,\n"
    "p3,Green Pen,office,2,USD,false,\n"
)

#p1: 3 views, 1 cart, 1 purchase
#p2: 1 view, 2 carts
#p3 has no events
EVENTS_A = (
    "event_id,shopper_id,product_id,event,timestamp\n"
    "e1,u1,p1,view,2026-10-01T10:00:00Z\n"
    "e2,u2,p1,view,2026-10-01T11:00:00Z\n"
    "e3,u3,p1,view,2026-10-01T12:00:00Z\n"
    "e4,u1,p1,cart,2026-10-01T10:05:00Z\n"
    "e5,u1,p1,purchase,2026-10-01T10:10:00Z\n"
    "e6,u2,p2,view,2026-10-02T09:00:00Z\n"
    "e7,u2,p2,cart,2026-10-02T09:01:00Z\n"
    "e8,u3,p2,cart,2026-10-02T09:02:00Z\n"
)

#another store that also has a p1
CATALOG_B = (
    "product_id,name,category,price,currency,available,url\n"
    "p1,Blue Mug,kitchen,10,USD,true,\n"
    "p9,Other Store Item,misc,5,USD,true,\n"
)

EVENTS_B = (
    "event_id,shopper_id,product_id,event,timestamp\n"
    "b1,x1,p1,view,2026-10-01T10:00:00Z\n"
    "b2,x2,p1,view,2026-10-01T10:00:00Z\n"
    "b3,x3,p1,view,2026-10-01T10:00:00Z\n"
    "b4,x4,p1,view,2026-10-01T10:00:00Z\n"
    "b5,x5,p1,view,2026-10-01T10:00:00Z\n"
)

P1 = {"product_id": "p1", "name": "Blue Mug", "category": "kitchen", "views": 3, "carts": 1, "purchases": 1}
P2 = {"product_id": "p2", "name": "Red Lamp", "category": "home", "views": 1, "carts": 2, "purchases": 0}
P3 = {"product_id": "p3", "name": "Green Pen", "category": "office", "views": 0, "carts": 0, "purchases": 0}


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "store.sqlite3")
    store = EventStore(path)
    store.import_catalog("store-a", CATALOG_A)
    store.import_events("store-a", EVENTS_A)
    store.import_catalog("store-b", CATALOG_B)
    store.import_events("store-b", EVENTS_B)
    return path


def by_id(result):
    #turn the list into a dict so we can do products["p1"]
    products = {}
    for item in result["items"]:
        products[item["product_id"]] = item
    return products


def test_S2_07_counts_match_fixture(db_path):
    products = by_id(get_product_stats(db_path, "store-a"))

    assert products["p1"] == P1
    assert products["p2"] == P2


def test_S2_07_product_with_no_events_shows_zeros(db_path):
    products = by_id(get_product_stats(db_path, "store-a"))

    assert products["p3"] == P3


def test_S2_07_reimport_does_not_inflate(db_path):
    #same file imported a second time
    EventStore(db_path).import_events("store-a", EVENTS_A)

    products = by_id(get_product_stats(db_path, "store-a"))

    assert products["p1"] == P1
    assert products["p2"] == P2


def test_S2_07_other_store_excluded(db_path):
    result = get_product_stats(db_path, "store-a")

    ids = []
    for item in result["items"]:
        ids.append(item["product_id"])

    assert ids == ["p1", "p2", "p3"]
    assert by_id(result)["p1"]["views"] == 3


def test_S2_07_pages_cover_every_product_once(db_path):
    page_1 = get_product_stats(db_path, "store-a", limit=2, offset=0)
    page_2 = get_product_stats(db_path, "store-a", limit=2, offset=2)

    assert page_1["items"] == [P1, P2]
    assert page_2["items"] == [P3]
    assert page_1["total"] == 3
    assert page_2["total"] == 3


def test_S2_07_empty_pages_and_unknown_store(db_path):
    past_end = get_product_stats(db_path, "store-a", limit=2, offset=3)
    assert past_end["items"] == []
    assert past_end["total"] == 3

    unknown = get_product_stats(db_path, "nope")
    assert unknown["items"] == []
    assert unknown["total"] == 0


def test_S2_07_api_returns_json(db_path, tmp_path):
    client = TestClient(create_app(db_path))

    response = client.get("/stores/store-a/products/stats")

    assert response.status_code == 200
    assert response.json() == {"items": [P1, P2, P3], "total": 3, "limit": 50, "offset": 0}

    #a brand new database with nothing imported yet
    new_client = TestClient(create_app(str(tmp_path / "new.sqlite3")))
    response = new_client.get("/stores/store-a/products/stats")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 50, "offset": 0}


def test_S2_07_api_rejects_bad_paging(db_path):
    client = TestClient(create_app(db_path))

    for query in ["limit=0", "limit=101", "offset=-1"]:
        response = client.get("/stores/store-a/products/stats?" + query)
        assert response.status_code == 422
