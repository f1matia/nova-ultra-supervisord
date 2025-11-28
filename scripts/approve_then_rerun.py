import os, sys, requests, json
BASE = os.getenv("BASE_URL","http://localhost:8000")
API_KEY = os.getenv("API_KEY_DEV","devkey")
H = {"X-API-Key": API_KEY, "Content-Type":"application/json"}

def approvals():
    r = requests.get(f"{BASE}/v1/human/approvals?status=pending", headers=H, timeout=10); r.raise_for_status()
    return r.json().get("items", [])

def decide(aid: str, decision="approve"):
    r = requests.post(f"{BASE}/v1/human/approvals/{aid}", headers=H, data=json.dumps({"decision":decision}), timeout=10); r.raise_for_status()
    return r.json()

def rerun(goal: str):
    body = {"user_id":"script","goal":goal,"allowed_tools":["web.search","rag.query"],"context":{},"constraints":{},"autonomy":{"enabled":True,"max_steps":3,"human_gate":[]}}
    r = requests.post(f"{BASE}/v1/nova/act/stream", headers=H, data=json.dumps(body), timeout=30, stream=True); r.raise_for_status()
    for line in r.iter_lines():
        if line: print(line.decode())

if __name__ == "__main__":
    items = approvals()
    if not items:
        print("No pending approvals"); sys.exit(0)
    aid = items[0]["id"]; print("Approving", aid); decide(aid, "approve")
    goal = items[0].get("payload",{}).get("goal","demo")
    print("Rerunning with goal:", goal); rerun(goal)
