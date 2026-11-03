"""Transactional catalog persistence for the local store import service."""
import csv
import io
import sqlite3
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
import re


class ImportValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('CSV validation failed')


def error(line, field, message):
    return {'line': line, 'field': field, 'message': message}


def read_csv(text, columns):
    reader = csv.reader(io.StringIO(text.lstrip('\ufeff'), newline=''), strict=True)
    try:
        header = next(reader, [])
        if len(header) != len(columns) or set(header) != set(columns):
            raise ImportValidationError([error(1, 'header', 'Expected: ' + ','.join(columns))])
        rows = []
        for values in reader:
            line = reader.line_num
            if len(values) != len(header):
                raise ImportValidationError([error(line, 'row', 'Wrong number of fields')])
            rows.append((line, dict(zip(header, (v.strip() for v in values)))))
        return rows
    except csv.Error as exc:
        raise ImportValidationError([error(reader.line_num, 'row', str(exc))]) from exc


def store_key(value):
    if not isinstance(value, str) or not value.strip():
        raise ImportValidationError([error(0, 'store_id', 'Store ID must not be blank')])
    return value.strip()


class CatalogStore:
    COLUMNS = ('product_id', 'name', 'category', 'price', 'currency', 'available', 'url')

    def __init__(self, path):
        self.path = str(path)
        if self.path == ':memory:':
            raise ValueError('Use a persistent database file')
        with self.connection() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS products (
                store_id TEXT NOT NULL, product_id TEXT NOT NULL, name TEXT NOT NULL,
                category TEXT NOT NULL, price TEXT NOT NULL, currency TEXT NOT NULL,
                available INTEGER NOT NULL, url TEXT NOT NULL,
                PRIMARY KEY (store_id, product_id))''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def import_catalog(self, store_id, text):
        store_id = store_key(store_id)
        rows = read_csv(text, self.COLUMNS)
        errors, seen = [], set()
        for line, row in rows:
            for field in ('product_id', 'name'):
                if not row[field]:
                    errors.append(error(line, field, 'Must not be blank'))
            if row['product_id'] in seen:
                errors.append(error(line, 'product_id', 'Duplicate ID in file'))
            seen.add(row['product_id'])
            try:
                price = Decimal(row['price'])
                if not price.is_finite() or price < 0:
                    raise InvalidOperation
            except InvalidOperation:
                errors.append(error(line, 'price', 'Expected finite nonnegative decimal'))
            if not re.fullmatch(r'[A-Z]{3}', row['currency']):
                errors.append(error(line, 'currency', 'Expected three uppercase ASCII letters'))
            if row['available'].lower() not in ('true', 'false'):
                errors.append(error(line, 'available', 'Expected true or false'))
            if row['url']:
                try:
                    url = urlsplit(row['url'])
                    valid = url.scheme in ('http', 'https') and bool(url.hostname) and not any(c.isspace() for c in row['url'])
                except ValueError:
                    valid = False
                if not valid:
                    errors.append(error(line, 'url', 'Expected HTTP(S) URL with host'))
        if errors:
            raise ImportValidationError(errors)
        inserted = updated = 0
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            for _, row in rows:
                exists = db.execute('SELECT 1 FROM products WHERE store_id=? AND product_id=?', (store_id, row['product_id'])).fetchone()
                updated += int(bool(exists))
                inserted += int(not exists)
                values = [row[c] for c in self.COLUMNS]
                values[5] = int(row['available'].lower() == 'true')
                db.execute('''INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(store_id,product_id) DO UPDATE SET
                    name=excluded.name, category=excluded.category, price=excluded.price,
                    currency=excluded.currency, available=excluded.available, url=excluded.url''',
                    [store_id] + values)
        return {'inserted': inserted, 'updated': updated}

    def list_products(self, store_id, limit=50, offset=0):
        store_id = store_key(store_id)
        if type(limit) is not int or type(offset) is not int or not 1 <= limit <= 100 or offset < 0:
            raise ImportValidationError([error(0, 'pagination', 'limit must be 1–100 and offset nonnegative')])
        with self.connection() as db:
            total = db.execute('SELECT COUNT(*) FROM products WHERE store_id=?', (store_id,)).fetchone()[0]
            rows = db.execute('SELECT product_id,name,category,price,currency,available,url FROM products WHERE store_id=? ORDER BY product_id LIMIT ? OFFSET ?', (store_id, limit, offset)).fetchall()
        items = [dict(row) for row in rows]
        for item in items:
            item['available'] = bool(item['available'])
        return {'items': items, 'total': total, 'limit': limit, 'offset': offset}
