"""Per-store API keys for the store import service (S3-04)."""
import hashlib
import hmac
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from fastapi.responses import JSONResponse

from .catalog_store import error, store_key

STORE_PATH = re.compile(r'^/stores/([^/]+)(?:/|$)')
BEARER = re.compile(r'^bearer +(\S+)$', re.IGNORECASE)


def digest(key):
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


class StoreKeys:
    def __init__(self, path):
        self.path = str(path)
        with self.connection() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS store_keys (
                store_id TEXT PRIMARY KEY, key_hash TEXT NOT NULL, created_at TEXT NOT NULL)''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def create_key(self, store_id):
        """Create (or replace) the store's key and return it. It is not recoverable later."""
        store_id = store_key(store_id)
        key = 'mk_' + secrets.token_urlsafe(32)
        created = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        with self.connection() as db:
            db.execute('''INSERT INTO store_keys VALUES (?, ?, ?)
                ON CONFLICT(store_id) DO UPDATE SET
                key_hash=excluded.key_hash, created_at=excluded.created_at''',
                (store_id, digest(key), created))
        return key

    def verify(self, store_id, key):
        if not isinstance(store_id, str) or not store_id.strip():
            return False
        if not isinstance(key, str) or not key:
            return False
        with self.connection() as db:
            row = db.execute('SELECT key_hash FROM store_keys WHERE store_id=?', (store_id.strip(),)).fetchone()
        # Compare against a dummy digest for unknown stores so both paths do the same work.
        stored = row[0] if row else digest('')
        return hmac.compare_digest(stored, digest(key)) and row is not None


def denied(status_code, message):
    headers = {'WWW-Authenticate': 'Bearer'} if status_code == 401 else None
    return JSONResponse(status_code=status_code, headers=headers,
                        content={'errors': [error(0, 'authorization', message)]})


def require_store_keys(app, db_path):
    """Make every /stores/{store_id}/... request on `app` present that store's key."""
    keys = StoreKeys(db_path)

    @app.middleware('http')
    async def check_store_key(request, call_next):
        match = STORE_PATH.match(request.scope['path'])
        if match:
            header = BEARER.match(request.headers.get('authorization', '').strip())
            if not header:
                return denied(401, 'Missing store API key')
            if not keys.verify(match.group(1), header.group(1)):
                return denied(403, 'Invalid store API key')
        return await call_next(request)

    return app
