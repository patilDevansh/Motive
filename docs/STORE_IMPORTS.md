# Local store import service

Install `python -m pip install -r requirements-imports.txt` and run `python -m uvicorn api.store:app --host 127.0.0.1`. Open `/docs` for the API. Set `MOTIVE_STORE_DB` to a persistent SQLite file if the default `motive-store.sqlite3` is unsuitable. Do not bind publicly until store-owner authentication is implemented: a store identifier isolates data, but is not an authorization credential.

POST raw UTF-8 CSV with Content-Type text/csv to `/stores/{store_id}/catalog/import`. Header:

```csv
product_id,name,category,price,currency,available,url
p1,Chair,Home,12.50,USD,true,https://example.com/p1
```

The response reports inserted and updated counts. Validation returns HTTP 400 with line/field/message errors and no partial writes. Product reads use GET `/stores/{store_id}/products?limit=50&offset=0`. The implementation and complete edge-case contract are in the S2-03 task specification. This service is independent of the Retailrocket model API and needs no model artifacts.

Event imports require catalog products first. POST text/csv to `/stores/{store_id}/events/import`:

```csv
event_id,shopper_id,product_id,event,timestamp
e1,u1,p1,view,2026-11-03T10:00:00-08:00
```

Events are `view`, `cart`, or `purchase`. Timestamps must include a timezone and are stored in UTC. GET `/stores/{store_id}/events` returns them in timestamp order. Identical event IDs skip; conflicting IDs reject the whole file. These endpoints are local development interfaces and require owner authentication before public deployment.
