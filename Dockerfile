FROM python:3.11-slim

# set workdir to backend code location inside image
WORKDIR /repo/backend

# install system deps and supervisor
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential git curl supervisor libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# copy backend sources into image
COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt

# install python deps
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r backend/requirements.txt

# copy supervisord.conf (expected under backend/)
COPY backend/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /repo/backend

EXPOSE 8000

# command: supervisord manages uvicorn + celery
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
