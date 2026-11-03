import pytest
from fastapi.testclient import TestClient
from src.catalog_store import CatalogStore, ImportValidationError
from src.event_store import EventStore
from api.store import create_app

PRODUCT = 'product_id,name,category,price,currency,available,url\np1,Chair,Home,10,USD,true,\n'
HEADER = 'event_id,shopper_id,product_id,event,timestamp\n'
def csv(*rows): return HEADER + ''.join(','.join(row)+'\n' for row in rows)
A = ('e1','u1','p1','view','2026-11-03T10:00:00-08:00')

@pytest.fixture
def store(tmp_path):
    s = EventStore(tmp_path/'db.sqlite3')
    s.import_catalog('a', PRODUCT)
    return s

@pytest.mark.parametrize('change,field', [(('product_id','other'),'product_id'),(('event','bad'),'event'),(('timestamp','2026-11-03T10:00:00'),'timestamp'),(('shopper_id',''),'shopper_id')], ids=['S2-04-AC1-unknown','S2-04-AC1-event','S2-04-AC1-time','S2-04-AC1-blank'])
def test_S2_04_invalid_rollback(store,change,field):
    bad=list(A); bad[list(EventStore.EVENT_COLUMNS).index(change[0])]=change[1]
    with pytest.raises(ImportValidationError) as ex:
        store.import_events('a',csv(A, bad))
    assert any(e['line']==3 and e['field']==field for e in ex.value.errors)
    assert store.list_events('a') == []


def test_S2_04_idempotent_offsets(store):
    assert store.import_events('a',csv(A)) == {'inserted':1,'skipped':0}
    equivalent=list(A); equivalent[-1]='2026-11-03T18:00:00Z'
    assert store.import_events('a',csv(equivalent)) == {'inserted':0,'skipped':1}
    assert len(store.list_events('a')) == 1


def test_S2_04_conflicting_ids(store):
    store.import_events('a',csv(A))
    conflicting=list(A); conflicting[3]='cart'
    fresh=('e2','u1','p1','view','2026-11-03T18:01:00Z')
    with pytest.raises(ImportValidationError): store.import_events('a',csv(fresh, conflicting))
    assert [r['event_id'] for r in store.list_events('a')] == ['e1']
    with pytest.raises(ImportValidationError): store.import_events('a',csv(A, conflicting))


def test_S2_04_restart_utc(store):
    store.import_events('a',csv(A))
    assert EventStore(store.path).list_events('a')[0]['timestamp']=='2026-11-03T18:00:00Z'
    assert store.import_events('a',csv(A,A)) == {'inserted':0,'skipped':2}


def test_S2_04_store_and_http(tmp_path):
    client=TestClient(create_app(tmp_path/'http.sqlite3'))
    assert client.post('/stores/a/catalog/import',content=PRODUCT,headers={'Content-Type':'text/csv'}).status_code==200
    assert client.post('/stores/b/catalog/import',content=PRODUCT,headers={'Content-Type':'text/csv'}).status_code==200
    url='/stores/a/events/import'
    assert client.post(url,content=csv(A),headers={'Content-Type':'text/csv'}).json()=={'inserted':1,'skipped':0}
    assert client.get('/stores/a/events').json()[0]['event_id']=='e1'
    assert client.get('/stores/b/events').json()==[]
    assert client.post(url,content=csv(('e2','u','missing','view','2026-11-03T18:00:00Z')),headers={'Content-Type':'text/csv'}).status_code==400
    assert client.post(url,content='',headers={'Content-Type':'text/csv'}).status_code==400
    assert client.post(url,content=HEADER,headers={'Content-Type':'text/csv'}).json()=={'inserted':0,'skipped':0}
