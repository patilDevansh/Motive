"""Local-only import API. Owner authentication is required before public deployment."""
import os
from fastapi import Body, FastAPI, Query
from fastapi.responses import JSONResponse
from src.catalog_store import CatalogStore, ImportValidationError
from src.event_store import EventStore
from src.product_event_stats import get_product_stats


def create_app(db_path):
    app = FastAPI(title='Motive local store imports')

    @app.exception_handler(ImportValidationError)
    async def validation_error(request, exc):
        return JSONResponse(status_code=400, content={'errors': exc.errors})

    @app.post('/stores/{store_id}/catalog/import')
    def import_catalog(store_id: str, body: str = Body('', media_type='text/csv')):
        return CatalogStore(db_path).import_catalog(store_id, body)

    @app.get('/stores/{store_id}/products')
    def products(store_id: str, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
        return CatalogStore(db_path).list_products(store_id, limit, offset)

    @app.get('/stores/{store_id}/products/stats')
    def product_stats(store_id: str, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
                      start: str | None = None, end: str | None = None):
        #makes the tables if the database is new
        EventStore(db_path)
        return get_product_stats(db_path, store_id, limit, offset, start, end)


    @app.post('/stores/{store_id}/events/import')
    def import_events(store_id: str, body: str = Body('', media_type='text/csv')):
        return EventStore(db_path).import_events(store_id, body)

    @app.get('/stores/{store_id}/events')
    def events(store_id: str):
        return EventStore(db_path).list_events(store_id)

    return app


app = create_app(os.environ.get('MOTIVE_STORE_DB', 'motive-store.sqlite3'))
