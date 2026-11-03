"""Store-scoped durable event ingestion."""
from datetime import datetime, timezone
from .catalog_store import CatalogStore, ImportValidationError, error, read_csv, store_key


class EventStore(CatalogStore):
    EVENT_COLUMNS = ('event_id', 'shopper_id', 'product_id', 'event', 'timestamp')

    def __init__(self, path):
        super().__init__(path)
        with self.connection() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS events (
                store_id TEXT NOT NULL, event_id TEXT NOT NULL, shopper_id TEXT NOT NULL,
                product_id TEXT NOT NULL, event TEXT NOT NULL, timestamp TEXT NOT NULL,
                PRIMARY KEY(store_id,event_id),
                FOREIGN KEY(store_id,product_id) REFERENCES products(store_id,product_id))''')

    def import_events(self, store_id, text):
        store_id = store_key(store_id)
        rows = read_csv(text, self.EVENT_COLUMNS)
        errors, parsed, in_file = [], [], {}
        with self.connection() as db:
            known = {r[0] for r in db.execute('SELECT product_id FROM products WHERE store_id=?', (store_id,))}
            existing = {r['event_id']: tuple(r[c] for c in self.EVENT_COLUMNS) for r in db.execute('SELECT event_id,shopper_id,product_id,event,timestamp FROM events WHERE store_id=?', (store_id,))}
        for line, row in rows:
            for field in self.EVENT_COLUMNS:
                if not row[field]: errors.append(error(line, field, 'Must not be blank'))
            if row['product_id'] and row['product_id'] not in known:
                errors.append(error(line, 'product_id', 'Unknown product in store'))
            if row['event'] and row['event'] not in ('view', 'cart', 'purchase'):
                errors.append(error(line, 'event', 'Expected view, cart, or purchase'))
            if row['timestamp']:
                try:
                    dt = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError
                    row['timestamp'] = dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
                except ValueError:
                    errors.append(error(line, 'timestamp', 'Expected ISO 8601 with timezone'))
            record = tuple(row[c] for c in self.EVENT_COLUMNS)
            id = row['event_id']
            if id in in_file and in_file[id] != record:
                errors.append(error(line, 'event_id', 'Conflicting ID in file'))
            if id in existing and existing[id] != record:
                errors.append(error(line, 'event_id', 'Conflicting stored ID'))
            in_file[id] = record
            parsed.append((line, record))
        if errors: raise ImportValidationError(errors)
        inserted = skipped = 0
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            for _, record in parsed:
                if record[0] in existing:
                    skipped += 1
                    continue
                db.execute('INSERT INTO events VALUES (?,?,?,?,?,?)', (store_id,) + record)
                existing[record[0]] = record
                inserted += 1
        return {'inserted': inserted, 'skipped': skipped}

    def list_events(self, store_id):
        store_id = store_key(store_id)
        with self.connection() as db:
            return [dict(r) for r in db.execute('SELECT event_id,shopper_id,product_id,event,timestamp FROM events WHERE store_id=? ORDER BY timestamp,event_id', (store_id,))]
