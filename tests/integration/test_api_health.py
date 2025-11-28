import requests, os
BASE=os.getenv('BASE_URL','http://localhost:8000')

def test_health():
 r=requests.get(f'{BASE}/healthz',timeout=5); assert r.status_code==200 and 'ok' in r.text
