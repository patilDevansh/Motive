import pytest
from fastapi.testclient import TestClient

from api.store import create_app
from src.event_store import EventStore
from src.product_event_stats import get_product_stats

URL = "/stores/store-a/products/stats"

START = "2026-10-01T00:00:00Z"
END = "2026-10-08T00:00:00Z"

CATALOG = (
    "product_id,name,category,price,currency,available,url\n"
    "p1,Blue Mug,kitchen,10,USD,true,\n"
    "p2,Red Lamp,home,25,USD,true,\n"
)

EVENTS = (
    "event_id,shopper_id,product_id,event,timestamp\n"
    "e1,u1,p1,view,2026-09-30T23:59:59.999Z\n"
    "e2,u1,p1,view,2026-10-01T00:00:00Z\n"
    "e3,u2,p1,view,2026-10-05T12:00:00Z\n"
    "e4,u3,p1,view,2026-10-07T23:59:59.999Z\n"
    "e5,u4,p1,view,2026-10-08T00:00:00Z\n"
    "e6,u2,p1,purchase,2026-10-06T00:00:00Z\n"
    "e7,u5,p2,view,2026-11-01T00:00:00Z\n"
)


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "store.sqlite3")
    store = EventStore(path)
    store.import_catalog("store-a", CATALOG)
    store.import_events("store-a", EVENTS)
    return path


@pytest.fixture
def client(db_path):
    return TestClient(create_app(db_path))


def p1(result):
    #find p1 in the list of products
    for item in result["items"]:
        if item["product_id"] == "p1":
            return item


def test_S2_08_event_at_start_is_counted(db_path):
    result = get_product_stats(db_path, "store-a", start=START, end=END)

    #e2 (exactly at start), e3 and e4 count, e1 is 1 ms too early
    assert p1(result)["views"] == 3
    assert p1(result)["purchases"] == 1


def test_S2_08_event_at_end_is_not_counted(db_path):
    result = get_product_stats(db_path, "store-a", start=START, end=END)
    assert p1(result)["views"] == 3

    #1 ms later so e5 is inside now
    result = get_product_stats(db_path, "store-a", start=START, end="2026-10-08T00:00:00.001Z")
    assert p1(result)["views"] == 4


def test_S2_08_equivalent_offsets_match(client):
    utc = client.get(URL, params={"start": START, "end": END})
    pacific = client.get(URL, params={
        "start": "2026-09-30T17:00:00-07:00",
        "end": "2026-10-07T17:00:00-07:00",
    })

    assert utc.status_code == 200
    assert pacific.status_code == 200
    assert utc.json() == pacific.json()
    assert p1(utc.json())["views"] == 3


def test_S2_08_omitted_bounds(db_path):
    only_start = get_product_stats(db_path, "store-a", start="2026-09-30T00:00:00Z")
    assert p1(only_start)["views"] == 5

    only_end = get_product_stats(db_path, "store-a", end="2026-10-05T12:00:00Z")
    assert p1(only_end)["views"] == 2

    neither = get_product_stats(db_path, "store-a")
    assert p1(neither)["views"] == 5


def test_S2_08_empty_window_returns_zeros(db_path):
    result = get_product_stats(db_path, "store-a", start="2026-12-01T00:00:00Z", end="2026-12-02T00:00:00Z")

    assert result["total"] == 2
    for item in result["items"]:
        assert item["views"] == 0
        assert item["carts"] == 0
        assert item["purchases"] == 0


def test_S2_08_rejects_start_not_before_end(client):
    same = client.get(URL, params={"start": START, "end": START})
    backwards = client.get(URL, params={"start": END, "end": START})

    for response in [same, backwards]:
        assert response.status_code == 400
        assert response.json() == {
            "errors": [{"line": 0, "field": "start", "message": "start must be before end"}]
        }


def test_S2_08_rejects_bad_timestamps(client):
    response = client.get(URL, params={"start": "yesterday"})
    assert response.status_code == 400
    assert response.json() == {
        "errors": [{"line": 0, "field": "start", "message": "Expected ISO 8601 timestamp"}]
    }

    response = client.get(URL, params={"end": "2026-13-01T00:00:00Z"})
    assert response.status_code == 400
    assert response.json() == {
        "errors": [{"line": 0, "field": "end", "message": "Expected ISO 8601 timestamp"}]
    }

    response = client.get(URL, params={"start": "2026-10-01T00:00:00"})
    assert response.status_code == 400
    assert response.json() == {
        "errors": [{"line": 0, "field": "start", "message": "Expected ISO 8601 with timezone"}]
    }
