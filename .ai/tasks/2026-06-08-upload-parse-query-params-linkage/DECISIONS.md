# Decisions

- Postgres is authoritative for query params. Instance metadata remains a cache and runtime compatibility layer.
- Existing API response shapes stay unchanged: `PUT` returns `{"message": "success", "data": params}` and `GET` returns `{"params": ..., "message": "success"}`.
- The live verification uses a temporary superadmin created through `scripts/ensure_superadmin.py`.
- The live upload/parse verification stops after parse and row inspection; no full index is required for P2-1.
