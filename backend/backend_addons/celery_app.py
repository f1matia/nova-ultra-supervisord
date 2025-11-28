import os
from celery import Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery("nova_ultra", broker=REDIS_URL, backend=REDIS_URL)
app.conf.task_routes = {"tasks.*": {"queue": "nova"}}
