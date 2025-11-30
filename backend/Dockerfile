FROM python:3.11-slim

# install system deps needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements (when building with ./backend as context, this is just ./requirements.txt)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy backend source (relative to build context)
COPY . /app/

# ensure supervisor dir exists and copy the conf
RUN mkdir -p /etc/supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
