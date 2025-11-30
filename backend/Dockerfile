# backend/Dockerfile — use this file inside the backend/ folder
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app

# system deps and supervisor
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential supervisor \
  && rm -rf /var/lib/apt/lists/*

# install python deps
# Ensure you have requirements.txt in backend/
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy app source into image
COPY . /app

# copy supervisord config into correct place
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# expose uvicorn port
EXPOSE 8000

# start supervisord which will start uvicorn + celery
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
