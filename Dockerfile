# Use official Python image
FROM python:3.11-slim

WORKDIR /repo/backend

# install system deps + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl supervisor \
  && rm -rf /var/lib/apt/lists/*

# copy backend sources and requirements
COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt

# install python deps
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy supervisord config (expects backend/supervisord.conf)
COPY backend/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /repo/backend
EXPOSE 8000

# supervisord will run uvicorn and celery
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
