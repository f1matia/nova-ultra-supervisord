# backend/backend_addons/tasks.py
from celery import shared_task
import time

@shared_task
def add(x, y):
    print(f"[TASK] add({x},{y}) start")
    time.sleep(2)
    print(f"[TASK] add result: {x+y}")
    return x + y

