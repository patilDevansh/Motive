"""Local-only import API. Owner authentication is required before public deployment."""
import os
from fastapi import FastAPI, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile
from src.catalog_store import CatalogStore, ImportValidationError, error
from src.event_store import EventStore
from src.product_event_stats import get_product_stats

MAX_IMPORT_BYTES = 5 * 1024 * 1024
# Room for multipart boundaries and extra form fields around the file itself.
MULTIPART_OVERHEAD_BYTES = 64 * 1024


class UploadError(Exception):
    """A request whose CSV could not be read at all (S3-03)."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.errors = [error(0, 'file', message)]
        super().__init__(message)


def too_large(limit):
    megabytes = limit / (1024 * 1024)
    size = f'{megabytes:g} MB' if megabytes >= 1 else f'{limit} bytes'
    return UploadError(413, f'File is larger than {size}')


async def read_csv_upload(request, limit):
    """Return the CSV text from a raw text/csv body or a multipart `file` part."""
    content_type = request.headers.get('content-type', '').split(';')[0].strip().lower()
    declared = request.headers.get('content-length', '')
    if content_type == 'text/csv':
        if declared.isdigit() and int(declared) > limit:
            raise too_large(limit)
        data = await request.body()
    elif content_type == 'multipart/form-data':
        if declared.isdigit() and int(declared) > limit + MULTIPART_OVERHEAD_BYTES:
            raise too_large(limit)
        try:
            form = await request.form()
        except Exception as exc:  # malformed multipart body
            raise UploadError(400, 'Upload the CSV in a file field named file') from exc
        upload = form.get('file')
        if not isinstance(upload, UploadFile):
            raise UploadError(400, 'Upload the CSV in a file field named file')
        data = await upload.read(limit + 1)
    else:
        raise UploadError(415, 'Send text/csv or multipart/form-data')
    if len(data) > limit:
        raise too_large(limit)
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise UploadError(400, 'File must be UTF-8 text') from exc


def create_app(db_path, max_import_bytes=MAX_IMPORT_BYTES):
    app = FastAPI(title='Motive local store imports')

    @app.exception_handler(ImportValidationError)
    async def validation_error(request, exc):
        return JSONResponse(status_code=400, content={'errors': exc.errors})

    @app.exception_handler(UploadError)
    async def upload_error(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'errors': exc.errors})

    @app.post('/stores/{store_id}/catalog/import')
    async def import_catalog(store_id: str, request: Request):
        text = await read_csv_upload(request, max_import_bytes)
        return await run_in_threadpool(CatalogStore(db_path).import_catalog, store_id, text)

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
    async def import_events(store_id: str, request: Request):
        text = await read_csv_upload(request, max_import_bytes)
        return await run_in_threadpool(EventStore(db_path).import_events, store_id, text)

    @app.get('/stores/{store_id}/events')
    def events(store_id: str):
        return EventStore(db_path).list_events(store_id)

    return app


app = create_app(os.environ.get('MOTIVE_STORE_DB', 'motive-store.sqlite3'))
