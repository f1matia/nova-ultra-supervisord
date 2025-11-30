FROM python:3.11-slim

# install system deps needed for building wheels (optional but helpful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy only requirements first to leverage docker cache
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy the rest of the backend
COPY backend/ /app/

# ensure supervisor dir exists and copy the conf
RUN mkdir -p /etc/supervisor
COPY backend/supervisord.conf /etc/supervisor/supervisord.conf

# Healthcheck (optional)
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -f http://localhost:8000/healthz || exit 1

# start supervisord in foreground
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
