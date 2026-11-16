import importlib
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.store import create_app
from src.catalog_store import ImportValidationError
from src.event_store import EventStore
from src.store_auth import StoreKeys, require_store_keys

ROOT = Path(__file__).resolve().parents[1]
CATALOG_HEADER = 'product_id,name,category,price,currency,available,url\n'
EVENTS_HEADER = 'event_id,shopper_id,product_id,event,timestamp\n'
RAW = {'Content-Type': 'text/csv'}
MISSING = {'errors': [{'line': 0, 'field': 'authorization', 'message': 'Missing store API key'}]}
INVALID = {'errors': [{'line': 0, 'field': 'authorization', 'message': 'Invalid store API key'}]}


def catalog(name):
    return CATALOG_HEADER + f'p1,{name},Home,10,USD,true,\n'


def events(event_id):
    return EVENTS_HEADER + f'{event_id},u1,p1,view,2026-11-10T18:00:00Z\n'


def bearer(key):
    return {'Authorization': 'Bearer ' + key}


def endpoints(store):
    """Every store endpoint as (method, url, request kwargs)."""
    return [
        ('POST', f'/stores/{store}/catalog/import', {'content': catalog('Changed'), 'headers': dict(RAW)}),
        ('GET', f'/stores/{store}/products', {'headers': {}}),
        ('GET', f'/stores/{store}/products/stats', {'headers': {}}),
        ('POST', f'/stores/{store}/events/import', {'content': events('e-new'), 'headers': dict(RAW)}),
        ('GET', f'/stores/{store}/events', {'headers': {}}),
    ]


def call(client, method, url, kwargs, auth=None):
    headers = dict(kwargs['headers'])
    if auth:
        headers.update(auth)
    return client.request(method, url, content=kwargs.get('content'), headers=headers)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / 'store.sqlite3'
    store = EventStore(path)
    store.import_catalog('a', catalog('Chair'))
    store.import_events('a', events('ea'))
    store.import_catalog('b', catalog('Secret Lamp'))
    store.import_events('b', events('eb'))
    return path


@pytest.fixture
def keys(db):
    return StoreKeys(db)


@pytest.fixture
def client(db):
    return TestClient(require_store_keys(create_app(db), db))


def snapshot(db, store):
    s = EventStore(db)
    return s.list_products(store), s.list_events(store)


def test_S3_04_key_format_and_storage(db, keys):
    first = keys.create_key('a')
    second = keys.create_key('b')
    assert first.startswith('mk_') and second.startswith('mk_')
    assert len(first) >= 40 and len(second) >= 40
    assert first != second
    con = sqlite3.connect(db)
    try:
        rows = con.execute('SELECT store_id, key_hash, created_at FROM store_keys ORDER BY store_id').fetchall()
    finally:
        con.close()
    assert [row[0] for row in rows] == ['a', 'b']
    for row in rows:
        assert first not in row and second not in row
        assert len(row[1]) == 64
    raw = Path(db).read_bytes()
    assert first.encode() not in raw and second.encode() not in raw


def test_S3_04_verify(db, keys):
    key_a = keys.create_key('a')
    reopened = StoreKeys(db)
    assert reopened.verify('a', key_a) is True
    assert reopened.verify(' a ', key_a) is True
    assert reopened.verify('a', key_a + 'x') is False
    assert reopened.verify('a', '') is False
    assert reopened.verify('a', None) is False
    assert reopened.verify('b', key_a) is False          # b has no key yet
    key_b = reopened.create_key('b')
    assert reopened.verify('a', key_b) is False          # another store's key
    assert reopened.verify('b', key_b) is True
    assert reopened.verify('', key_a) is False
    with pytest.raises(ImportValidationError):
        reopened.create_key('   ')


@pytest.mark.parametrize('auth', [None, {'Authorization': 'Basic abc'}, {'Authorization': 'Bearer'}, {'Authorization': 'Bearer '}],
                         ids=['S3-04-AC3-none', 'S3-04-AC3-basic', 'S3-04-AC3-bare', 'S3-04-AC3-empty'])
def test_S3_04_missing_key_is_401(client, keys, auth):
    keys.create_key('a')
    for method, url, kwargs in endpoints('a'):
        response = call(client, method, url, kwargs, auth)
        assert response.status_code == 401, url
        assert response.headers['www-authenticate'] == 'Bearer'
        assert response.json() == MISSING


def test_S3_04_own_key_allows_every_endpoint(client, keys):
    auth = bearer(keys.create_key('a'))
    r = client.post('/stores/a/catalog/import', content=catalog('Desk'), headers={**RAW, **auth})
    assert r.status_code == 200 and r.json() == {'inserted': 0, 'updated': 1}
    r = client.get('/stores/a/products', headers=auth)
    assert r.status_code == 200 and r.json()['items'][0]['name'] == 'Desk'
    r = client.post('/stores/a/events/import', content=events('e2'), headers={**RAW, **auth})
    assert r.status_code == 200 and r.json() == {'inserted': 1, 'skipped': 0}
    r = client.get('/stores/a/products/stats', headers=auth)
    assert r.status_code == 200 and r.json()['items'][0]['views'] == 2
    r = client.get('/stores/a/events', headers=auth)
    assert r.status_code == 200 and [e['event_id'] for e in r.json()] == ['e2', 'ea']
    lower = client.get('/stores/a/products', headers={'Authorization': 'bearer ' + auth['Authorization'][7:]})
    assert lower.status_code == 200


def test_S3_04_other_store_key_is_403(client, keys, db):
    auth = bearer(keys.create_key('a'))
    keys.create_key('b')
    before = snapshot(db, 'b')
    for store in ('b', '%62', 'nokey'):
        for method, url, kwargs in endpoints(store):
            response = call(client, method, url, kwargs, auth)
            assert response.status_code == 403, url
            assert response.json() == INVALID
            assert 'Secret Lamp' not in response.text
    assert snapshot(db, 'b') == before
    assert client.get('/stores/%61/products', headers=auth).status_code == 200   # encoded own store


def test_S3_04_rotation_revokes_old_key(client, keys):
    old = keys.create_key('a')
    assert client.get('/stores/a/products', headers=bearer(old)).status_code == 200
    new = keys.create_key('a')
    assert new != old
    revoked = client.get('/stores/a/products', headers=bearer(old))
    assert revoked.status_code == 403 and revoked.json() == INVALID
    assert client.get('/stores/a/products', headers=bearer(new)).status_code == 200


@pytest.mark.parametrize('path,body', [
    ('catalog/import', 'not,a,catalog\n'),
    ('catalog/import', catalog('Overwritten')),
    ('events/import', 'bad\n'),
    ('events/import', events('e-forbidden')),
], ids=['S3-04-AC7-catalog-invalid', 'S3-04-AC7-catalog-valid', 'S3-04-AC7-events-invalid', 'S3-04-AC7-events-valid'])
def test_S3_04_rejected_import_stores_nothing(client, keys, db, path, body):
    keys.create_key('a')
    wrong = bearer(keys.create_key('b'))
    before = snapshot(db, 'a')
    no_key = client.post(f'/stores/a/{path}', content=body, headers=RAW)
    assert no_key.status_code == 401 and no_key.json() == MISSING
    wrong_key = client.post(f'/stores/a/{path}', content=body, headers={**RAW, **wrong})
    assert wrong_key.status_code == 403 and wrong_key.json() == INVALID
    assert snapshot(db, 'a') == before


def test_S3_04_disabled_by_default(db, keys, monkeypatch):
    keys.create_key('a')
    open_client = TestClient(create_app(db))
    assert open_client.get('/stores/a/products').status_code == 200
    assert open_client.get('/stores/a/products', headers=bearer('mk_wrong')).status_code == 200
    assert open_client.post('/stores/a/events/import', content=events('e3'), headers=RAW).status_code == 200

    import api.store as module
    monkeypatch.setenv('MOTIVE_STORE_DB', str(db))
    try:
        for value, expected in [(None, 200), ('off', 200), ('Required', 401)]:
            if value is None:
                monkeypatch.delenv('MOTIVE_STORE_AUTH', raising=False)
            else:
                monkeypatch.setenv('MOTIVE_STORE_AUTH', value)
            reloaded = TestClient(importlib.reload(module).app)
            assert reloaded.get('/stores/a/products').status_code == expected, value
            assert reloaded.get('/openapi.json').status_code == 200
    finally:
        monkeypatch.undo()
        importlib.reload(module)


def test_S3_04_cli_prints_working_key(db):
    result = subprocess.run([sys.executable, '-m', 'scripts.create_store_key', 'a', '--db', str(db)],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 1 and lines[0].startswith('mk_')
    assert StoreKeys(db).verify('a', lines[0]) is True
    assert StoreKeys(db).verify('b', lines[0]) is False
