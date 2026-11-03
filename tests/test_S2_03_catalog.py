import csv
import io
import pytest
from fastapi.testclient import TestClient
from api.store import create_app
from src.catalog_store import CatalogStore, ImportValidationError

HEADER = 'product_id,name,category,price,currency,available,url\n'
ROW = ['p1', 'Chair', 'Home', '12.50', 'USD', 'true', 'https://example.com/p1']


def catalog(*rows):
    out = io.StringIO()
    out.write(HEADER)
    csv.writer(out).writerows(rows)
    return out.getvalue()


@pytest.fixture
def store(tmp_path):
    return CatalogStore(tmp_path / 'store.sqlite3')


@pytest.mark.parametrize('case', ['S2-03-AC1-restart'])
def test_S2_03_restart(store, case):
    assert store.import_catalog('a', catalog(ROW)) == {'inserted': 1, 'updated': 0}
    item = CatalogStore(store.path).list_products('a')['items'][0]
    assert item == dict(zip(CatalogStore.COLUMNS, ROW[:5] + [True] + ROW[6:]))


@pytest.mark.parametrize('field,value', [('product_id',''), ('name',''), ('price','NaN'), ('price','-1'), ('currency','usd'), ('available','maybe'), ('url','ftp://example.com')], ids=lambda v: 'S2-03-AC2-' + v)
def test_S2_03_invalid_rollback(store, field, value):
    store.import_catalog('a', catalog(ROW))
    bad = ROW.copy(); bad[CatalogStore.COLUMNS.index(field)] = value
    good = ROW.copy(); good[0] = 'p2'
    with pytest.raises(ImportValidationError) as exc:
        store.import_catalog('a', catalog(good, bad))
    assert any(e['line'] == 3 and e['field'] == field for e in exc.value.errors)
    assert store.list_products('a')['total'] == 1
    assert store.list_products('a')['items'][0]['name'] == 'Chair'


@pytest.mark.parametrize('case', ['S2-03-AC3-upsert'])
def test_S2_03_upsert(store, case):
    store.import_catalog('a', catalog(ROW))
    changed = ROW.copy(); changed[1] = 'Desk'
    assert store.import_catalog('a', catalog(changed)) == {'inserted': 0, 'updated': 1}
    assert store.list_products('a')['items'][0]['name'] == 'Desk'
    with pytest.raises(ImportValidationError):
        store.import_catalog('a', catalog(ROW, ROW))
    assert store.list_products('a')['items'][0]['name'] == 'Desk'


@pytest.mark.parametrize('case', ['S2-03-AC4-isolation'])
def test_S2_03_isolation(store, case):
    store.import_catalog('a', catalog(ROW))
    other = ROW.copy(); other[1] = 'Table'
    store.import_catalog('b', catalog(other))
    assert store.list_products('a')['items'][0]['name'] == 'Chair'
    assert store.list_products('b')['items'][0]['name'] == 'Table'
    assert store.list_products('c')['total'] == 0


@pytest.mark.parametrize('case', ['S2-03-AC5-pagination'])
def test_S2_03_pagination(store, case):
    store.import_catalog('a', catalog(*[[str(i)] + ROW[1:] for i in reversed(range(5))]))
    items = sum([store.list_products('a', 2, offset)['items'] for offset in (0,2,4)], [])
    assert [p['product_id'] for p in items] == list('01234')
    for limit, offset in [(0,0), (101,0), (2,-1), (True,0)]:
        with pytest.raises(ImportValidationError):
            store.list_products('a', limit, offset)


@pytest.mark.parametrize('case', ['S2-03-AC6-http'])
def test_S2_03_http_and_csv(tmp_path, case):
    client = TestClient(create_app(tmp_path / 'http.sqlite3'))
    url = '/stores/a/catalog/import'
    r = client.post(url, content='\ufeff'+catalog(ROW), headers={'Content-Type':'text/csv'})
    assert r.status_code == 200 and r.json() == {'inserted':1,'updated':0}
    assert client.get('/stores/a/products').json()['total'] == 1
    assert client.get('/stores/a/products?limit=0').status_code == 422
    assert client.post(url, content=HEADER, headers={'Content-Type':'text/csv'}).json() == {'inserted':0,'updated':0}
    for invalid in ['', 'wrong\n', HEADER+'short,row\n', HEADER+'"unterminated']:
        r = client.post(url, content=invalid, headers={'Content-Type':'text/csv'})
        assert r.status_code == 400
        if invalid:
            assert set(r.json()['errors'][0]) == {'line','field','message'}
    assert client.get('/stores/a/products').json()['total'] == 1
