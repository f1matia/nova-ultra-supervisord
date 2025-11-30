# Use official Python image
FROM python:3.11-slim

# set workdir
WORKDIR /repo/backend

# install system deps and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl supervisor \
  && rm -rf /var/lib/apt/lists/*

# copy backend sources
COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt

# install python deps
RUN pip install --no-cache-dir -r backend/requirements.txt

# copy supervisord.conf (if present in backend/)
COPY backend/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ensure working dir
WORKDIR /repo/backend

# expose http port
EXPOSE 8000

# default command: run supervisord which manages uvicorn + celery
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
