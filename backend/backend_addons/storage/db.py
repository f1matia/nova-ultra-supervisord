import os, json, uuid
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)

def init_tables():
    sql = '''
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE TABLE IF NOT EXISTS approvals (
        id UUID PRIMARY KEY,
        action TEXT NOT NULL,
        tool TEXT NOT NULL,
        payload JSONB NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        decided_at TIMESTAMPTZ
    );
    CREATE TABLE IF NOT EXISTS audit_log (
        id UUID PRIMARY KEY,
        event TEXT NOT NULL,
        payload JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );'''
    with get_conn() as c:
        c.execute(sql)

def insert_approval(action: str, tool: str, payload: dict) -> str:
    aid = str(uuid.uuid4())
    with get_conn() as c:
        c.execute("INSERT INTO approvals (id, action, tool, payload, status) VALUES (%s,%s,%s,%s,%s)",
                  (aid, action, tool, json.dumps(payload), "pending"))
    return aid

def update_approval(aid: str, status: str):
    with get_conn() as c:
        c.execute("UPDATE approvals SET status=%s, decided_at=now() WHERE id=%s", (status, aid))

def list_approvals(status: str = "pending"):
    with get_conn() as c:
        return c.execute("SELECT * FROM approvals WHERE status=%s ORDER BY created_at DESC", (status,)).fetchall()

def audit(event: str, payload: dict):
    with get_conn() as c:
        c.execute("INSERT INTO audit_log (id, event, payload) VALUES (gen_random_uuid(), %s, %s)",
                  (event, json.dumps(payload)))
