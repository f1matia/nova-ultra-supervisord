FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000


# Install supervisor and set up supervisord to run both uvicorn and celery in one container
RUN apt-get update && apt-get install -y --no-install-recommends supervisor && rm -rf /var/lib/apt/lists/*

# copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure working directory
WORKDIR /repo/backend

EXPOSE 8000

# Run supervisord (which will manage uvicorn + celery)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
