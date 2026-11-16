import pytest
from fastapi.testclient import TestClient
from api.store import MAX_IMPORT_BYTES, create_app

CATALOG_HEADER = 'product_id,name,category,price,currency,available,url\n'
CATALOG = CATALOG_HEADER + 'p1,Chair,Home,12.50,USD,true,https://example.com/p1\np2,Desk,Home,80,USD,false,\n'
EVENTS_HEADER = 'event_id,shopper_id,product_id,event,timestamp\n'
EVENTS = EVENTS_HEADER + 'e1,u1,p1,view,2026-11-10T10:00:00-08:00\ne2,u1,p2,cart,2026-11-10T18:05:00Z\n'
CATALOG_URL = '/stores/{}/catalog/import'
EVENTS_URL = '/stores/{}/events/import'
RAW = {'Content-Type': 'text/csv'}
NOT_UTF8 = CATALOG_HEADER.encode() + b'p1,Caf\xe9,Home,1,USD,true,\n'


def file_error(message):
    return {'errors': [{'line': 0, 'field': 'file', 'message': message}]}


def as_file(content, name='upload.csv'):
    if isinstance(content, str):
        content = content.encode('utf-8')
    return {'file': (name, content, 'text/csv')}


@pytest.fixture
def db(tmp_path):
    return tmp_path / 'store.sqlite3'


@pytest.fixture
def client(db):
    return TestClient(create_app(db))


def test_S3_03_catalog_multipart_matches_raw(client):
    uploaded = client.post(CATALOG_URL.format('a'), files=as_file(CATALOG))
    raw = client.post(CATALOG_URL.format('b'), content=CATALOG, headers=RAW)
    assert uploaded.status_code == 200 and raw.status_code == 200
    assert uploaded.json() == raw.json() == {'inserted': 2, 'updated': 0}
    listed = client.get('/stores/a/products').json()
    assert listed['total'] == 2
    assert [item['product_id'] for item in listed['items']] == ['p1', 'p2']
    assert listed['items'] == client.get('/stores/b/products').json()['items']
    # Extra form fields are ignored and a second upload updates the same rows.
    again = client.post(CATALOG_URL.format('a'), files=as_file(CATALOG), data={'note': 'ignored'})
    assert again.json() == {'inserted': 0, 'updated': 2}


def test_S3_03_events_multipart_import(client):
    assert client.post(CATALOG_URL.format('a'), files=as_file(CATALOG)).status_code == 200
    first = client.post(EVENTS_URL.format('a'), files=as_file(EVENTS))
    assert first.status_code == 200
    assert first.json() == {'inserted': 2, 'skipped': 0}
    stored = client.get('/stores/a/events').json()
    assert [(e['event_id'], e['product_id'], e['event'], e['timestamp']) for e in stored] == [
        ('e1', 'p1', 'view', '2026-11-10T18:00:00Z'),
        ('e2', 'p2', 'cart', '2026-11-10T18:05:00Z'),
    ]
    assert client.post(EVENTS_URL.format('a'), files=as_file(EVENTS)).json() == {'inserted': 0, 'skipped': 2}
    assert len(client.get('/stores/a/events').json()) == 2


def test_S3_03_multipart_invalid_row_stores_nothing(client):
    bad_catalog = CATALOG_HEADER + 'p1,Chair,Home,1,USD,true,\np2,Desk,Home,-5,USD,true,\n'
    response = client.post(CATALOG_URL.format('a'), files=as_file(bad_catalog))
    assert response.status_code == 400
    assert any(e['line'] == 3 and e['field'] == 'price' for e in response.json()['errors'])
    assert client.get('/stores/a/products').json()['total'] == 0

    assert client.post(CATALOG_URL.format('a'), files=as_file(CATALOG)).status_code == 200
    bad_events = EVENTS_HEADER + 'e1,u1,p1,view,2026-11-10T18:00:00Z\ne2,u1,missing,view,2026-11-10T18:00:00Z\n'
    response = client.post(EVENTS_URL.format('a'), files=as_file(bad_events))
    assert response.status_code == 400
    assert any(e['line'] == 3 and e['field'] == 'product_id' for e in response.json()['errors'])
    assert client.get('/stores/a/events').json() == []


@pytest.mark.parametrize('url', [CATALOG_URL, EVENTS_URL], ids=['S3-03-AC4-catalog', 'S3-03-AC4-events'])
def test_S3_03_missing_file_field(client, url):
    expected = file_error('Upload the CSV in a file field named file')
    wrong_name = client.post(url.format('a'), files={'upload': ('c.csv', CATALOG.encode(), 'text/csv')})
    assert wrong_name.status_code == 400
    assert wrong_name.json() == expected
    # `file` sent as an ordinary text field next to a real file part is not a file upload.
    text_field = client.post(url.format('a'), data={'file': CATALOG},
                             files={'other': ('c.csv', b'x', 'text/csv')})
    assert text_field.status_code == 400
    assert text_field.json() == expected
    assert client.get('/stores/a/products').json()['total'] == 0


def test_S3_03_rejects_non_utf8(client):
    expected = file_error('File must be UTF-8 text')
    uploaded = client.post(CATALOG_URL.format('a'), files=as_file(NOT_UTF8))
    assert uploaded.status_code == 400
    assert uploaded.json() == expected
    raw = client.post(CATALOG_URL.format('a'), content=NOT_UTF8, headers=RAW)
    assert raw.status_code == 400
    assert raw.json() == expected
    events = client.post(EVENTS_URL.format('a'), files=as_file(EVENTS_HEADER.encode() + b'\xff\xfe'))
    assert events.status_code == 400
    assert events.json() == expected
    assert client.get('/stores/a/products').json()['total'] == 0


def test_S3_03_size_limit(db):
    assert MAX_IMPORT_BYTES == 5 * 1024 * 1024
    limit = 200
    client = TestClient(create_app(db, max_import_bytes=limit))
    expected = file_error('File is larger than 200 bytes')
    row = 'p1,{},Home,1,USD,true,\n'
    exact = CATALOG_HEADER + row.format('x' * (limit - len(CATALOG_HEADER) - len(row.format(''))))
    assert len(exact.encode()) == limit
    over = exact.replace('x', 'xx', 1)
    assert len(over.encode()) == limit + 1

    too_big = client.post(CATALOG_URL.format('a'), files=as_file(over))
    assert too_big.status_code == 413
    assert too_big.json() == expected
    too_big_raw = client.post(CATALOG_URL.format('a'), content=over, headers=RAW)
    assert too_big_raw.status_code == 413
    assert too_big_raw.json() == expected
    too_big_events = client.post(EVENTS_URL.format('a'), files=as_file('e' * (limit + 1)))
    assert too_big_events.status_code == 413
    assert client.get('/stores/a/products').json()['total'] == 0

    assert client.post(CATALOG_URL.format('a'), files=as_file(exact)).json() == {'inserted': 1, 'updated': 0}
    assert client.post(CATALOG_URL.format('b'), content=exact, headers=RAW).json() == {'inserted': 1, 'updated': 0}


def test_S3_03_default_limit_message(db):
    client = TestClient(create_app(db))
    response = client.post(CATALOG_URL.format('a'), files=as_file(b'x' * (MAX_IMPORT_BYTES + 1)))
    assert response.status_code == 413
    assert response.json() == file_error('File is larger than 5 MB')


@pytest.mark.parametrize('url', [CATALOG_URL, EVENTS_URL], ids=['S3-03-AC7-catalog', 'S3-03-AC7-events'])
def test_S3_03_rejects_other_content_types(client, url):
    expected = file_error('Send text/csv or multipart/form-data')
    as_json = client.post(url.format('a'), json={'csv': CATALOG})
    assert as_json.status_code == 415
    assert as_json.json() == expected
    as_form = client.post(url.format('a'), data={'file': CATALOG})
    assert as_form.status_code == 415
    assert as_form.json() == expected
    assert client.get('/stores/a/products').json()['total'] == 0


def test_S3_03_multipart_bom(client):
    response = client.post(CATALOG_URL.format('a'), files=as_file('﻿' + CATALOG_HEADER + 'p1,Chair,Home,1,USD,true,\n'))
    assert response.status_code == 200
    assert response.json() == {'inserted': 1, 'updated': 0}
    assert client.get('/stores/a/products').json()['items'][0]['name'] == 'Chair'
