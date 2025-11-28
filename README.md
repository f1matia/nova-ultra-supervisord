# NOVA Ultra — Full MVP Bundle

This repo contains a runnable MVP: backend (FastAPI), single-file console (Nginx), pluggable vector DBs, SSE + NDJSON streaming, approvals, rate limiting, Celery worker, and integration tests.

## Quick start
```bash
docker compose --profile api --profile frontend up --build
# open http://localhost:5173 (Base URL defaults to http://localhost:8000)
```

### Add optional services
- pgvector: `--profile pg`
- weaviate: `--profile weaviate`
- redis + worker: `--profile redis --profile worker`

## Endpoints
- `GET /healthz`
- `GET /auth/dev/mint?role=user|admin`  (header: `X-API-Key: devkey`)
- `POST /v1/nova/act/stream` **(NDJSON)**
- `POST /v1/nova/act/sse` **(text/event-stream)**

## Scripts
- `scripts/approve_then_rerun.py` — approves first pending item, reruns stream.

## Frontends
- `frontend-nginx/` — single-file HTML console served by Nginx.
  - Buttons for NDJSON and SSE streaming.
  - Approvals fetch & display.

## Configuration
See `backend/.env`:
```dotenv
NOVA_VECDB=memory | pgvector | weaviate
DATABASE_URL=postgresql+psycopg://nova:nova@pg:5432/nova
WEAVIATE_URL=http://weaviate:8080
NOVA_WEBSEARCH=stub | real
LLM_PROVIDER=mock | openai | anthropic
REDIS_URL=redis://redis:6379/0
```
## Tests
Integration tests under `tests/integration` (use `pytest` with services running).
```bash
BASE_URL=http://localhost:8000 pytest -q tests/integration
```
