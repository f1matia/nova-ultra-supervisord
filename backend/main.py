import os, time, json, asyncio, secrets
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY_DEV = os.getenv("API_KEY_DEV", "devkey")
NOVA_WEBSEARCH = os.getenv("NOVA_WEBSEARCH", "stub")
NOVA_VECDB = os.getenv("NOVA_VECDB", "memory")

from backend_addons.routes.sse import router as sse_router
from backend_addons.storage.db import init_tables, list_approvals, update_approval
from backend_addons.rate_limit import allow as rl_allow

app = FastAPI(title="NOVA Ultra MVP", version="0.2.0")
app.include_router(sse_router)

@app.on_event("startup")
async def _startup():
    try:
        init_tables()
    except Exception as e:
        print("DB init skipped/failed:", e)

import jwt
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
JWT_ISSUER = os.getenv("JWT_ISSUER", "nova-ultra")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "nova-ultra-clients")

def check_auth(x_api_key: Optional[str], authorization: Optional[str], require_admin: bool = False):
    # Allow dev API key for quick testing
    if x_api_key == API_KEY_DEV:
        return
    # Validate JWT if provided
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience=JWT_AUDIENCE, issuer=JWT_ISSUER)
            if require_admin and payload.get("role") != "admin":
                raise HTTPException(403, "Admin role required")
            return
        except Exception as e:
            raise HTTPException(401, f"Invalid token: {e}")
    raise HTTPException(401, "Unauthorized")

@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"

APPROVALS: Dict[str, Dict[str, Any]] = {}

class Decision(BaseModel):
    decision: str

@app.get("/v1/human/approvals")
async def approvals(status: str = "pending", x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    check_auth(x_api_key, authorization)
    try:
        rows = list_approvals(status=status)
        items = rows
    except Exception:
        items = [v for v in APPROVALS.values() if v.get("status") == status]
    return {"items": items}

@app.post("/v1/human/approvals/{approval_id}")
async def decide(approval_id: str, body: Decision, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    check_auth(x_api_key, authorization)
    if body.decision not in ("approve","deny"):
        raise HTTPException(400, "invalid decision")
    try:
        update_approval(approval_id, "approved" if body.decision == "approve" else "denied")
        return {"ok": True, "id": approval_id, "status": body.decision}
    except Exception:
        if approval_id not in APPROVALS:
            raise HTTPException(404, "unknown approval")
        APPROVALS[approval_id]["status"] = "approved" if body.decision == "approve" else "denied"
        return {"ok": True, "id": approval_id, "status": APPROVALS[approval_id]["status"]}

@app.get("/auth/jwt/issue")
async def issue(role: str = "user", x_api_key: Optional[str] = Header(None)):
    # DEV issuer: in prod, integrate with your IdP
    if x_api_key != API_KEY_DEV:
        raise HTTPException(401, "invalid api key")
    import time, jwt
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + 3600,
        "role": role,
        "sub": "dev-user"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"token": token, "role": role}

@app.get("/auth/dev/mint")
async def mint(role: str = "user", x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY_DEV:
        raise HTTPException(401, "invalid api key")
    token = "dev." + role + "." + secrets.token_hex(16)
    return {"token": token, "role": role}

class Autonomy(BaseModel):
    enabled: bool = True
    max_steps: int = 3
    human_gate: List[str] = []

class ActBody(BaseModel):
    user_id: str
    goal: str
    allowed_tools: List[str] = []
    context: Dict[str, Any] = {}
    constraints: Dict[str, Any] = {}
    autonomy: Autonomy = Autonomy()

def jsonl(obj: Dict[str, Any]) -> bytes:
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode()

@app.post("/v1/nova/act/stream")
async def act_stream(body: ActBody, request: Request, x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    check_auth(x_api_key, authorization)
    if not rl_allow(f"user:{body.user_id}:stream", limit=60, window_sec=60):
        raise HTTPException(429, "rate limit")

    async def gen():
        yield jsonl({"event":"start","ts":int(time.time()),"data":{"goal":body.goal,"websearch":NOVA_WEBSEARCH,"vecdb":NOVA_VECDB}})
        steps = [
            {"intent":"understand_goal","tool":"reason","summary":f"Parsing goal: {body.goal}","risks":{"privacy":0.1,"safety":0.05,"bias":0.02}},
            {"intent":"gather_evidence","tool":"web.search" if "web.search" in body.allowed_tools else "rag.query","summary":"Collecting evidence (demo).","risks":{"privacy":0.12,"safety":0.06,"bias":0.02}},
            {"intent":"synthesize","tool":"reason","summary":"Drafting plan with context.","risks":{"privacy":0.1,"safety":0.05,"bias":0.02}},
        ]
        for s in steps[:max(1, body.autonomy.max_steps)]:
            await asyncio.sleep(0.25)
            yield jsonl({"event":"step","ts":int(time.time()),"data":s})
        if "deploy" in body.autonomy.human_gate:
            appr_id = secrets.token_hex(8)
            APPROVALS[appr_id] = {"id":appr_id,"action":"deploy_plan","tool":"ops.apply","payload":{"goal":body.goal},"status":"pending"}
            yield jsonl({"event":"approval","ts":int(time.time()),"data":{"approval_id":appr_id,"intent":"deploy_plan","tool":"ops.apply","summary":"Request to deploy.","risks":{"safety":0.25}}})
        yield jsonl({"event":"end","ts":int(time.time()),"summary":{"note":"NDJSON stream complete"}})

    return StreamingResponse(gen(), media_type="application/x-ndjson")
