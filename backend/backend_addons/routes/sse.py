import asyncio, json, time, secrets
from typing import Dict, Any, List
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
APPROVALS: Dict[str, Dict[str, Any]] = {}

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

def _sse(data: Dict[str, Any]) -> bytes:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode()

@router.post("/v1/nova/act/sse")
async def nova_act_sse(body: ActBody, request: Request, x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(401, "Missing API key")

    async def gen():
        yield _sse({"event":"start","ts":int(time.time()),"data":{"goal":body.goal}})
        steps = [
            {"intent":"understand_goal","tool":"reason","summary":f"Parsing goal: {body.goal}","risks":{"privacy":0.1}},
            {"intent":"gather_evidence","tool":"web.search","summary":"Collecting evidence (SSE demo).","risks":{"privacy":0.12}},
            {"intent":"synthesize","tool":"reason","summary":"Drafting plan.","risks":{"privacy":0.1}},
        ]
        for s in steps[:max(1, body.autonomy.max_steps)]:
            await asyncio.sleep(0.2)
            yield _sse({"event":"step","ts":int(time.time()),"data":s})

        if "deploy" in body.autonomy.human_gate:
            appr_id = secrets.token_hex(8)
            APPROVALS[appr_id] = {"id":appr_id,"action":"deploy_plan","tool":"ops.apply","payload":{"goal":body.goal},"status":"pending"}
            yield _sse({"event":"approval","ts":int(time.time()),"data":{"approval_id":appr_id,"intent":"deploy_plan","tool":"ops.apply","summary":"Approve deployment?"}})

        yield _sse({"event":"end","ts":int(time.time()),"summary":{"note":"SSE stream complete"}})

    return StreamingResponse(gen(), media_type="text/event-stream")
