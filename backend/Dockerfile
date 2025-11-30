# backend/Dockerfile  lightweight variant (no build-essential)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# install only supervisor (avoid heavy build-essential)
RUN apt-get update \
  && apt-get install -y --no-install-recommends supervisor \
  && rm -rf /var/lib/apt/lists/*

# install python deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy app source into image
COPY . /app

# copy supervisord config into correct place
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
