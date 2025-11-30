FROM python:3.11-slim

# avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# copy only requirements first (good cache behavior)
COPY requirements.txt /app/requirements.txt

# install system deps needed for some wheels (psycopg, build tools, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev curl && \
    python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apt-get remove -y build-essential gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# copy backend code into image
COPY . /app

# make sure python finds backend package (if your package layout expects this)
ENV PYTHONPATH=/app

# default command: run uvicorn (binds to $PORT if Render sets it)
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
