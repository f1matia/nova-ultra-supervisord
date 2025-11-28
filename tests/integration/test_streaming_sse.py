import os, json, requests
BASE=os.getenv('BASE_URL','http://localhost:8000')
def test_sse_stream():
    body={"user_id":"test","goal":"demo","allowed_tools":[],"context":{},"constraints":{},"autonomy":{"enabled":True,"max_steps":2,"human_gate":[]}}
    r=requests.post(f"{BASE}/v1/nova/act/sse", headers={"X-API-Key":"devkey","Content-Type":"application/json"}, data=json.dumps(body), stream=True, timeout=15)
    assert r.status_code==200
    got=False
    for chunk in r.iter_content(None):
        if b"data:" in chunk: got=True; break
    assert got
