from .celery_app import app
import time
@app.task
def run_agent(goal: str) -> str:
    time.sleep(1)
    return f"done: {goal[:64]}"
