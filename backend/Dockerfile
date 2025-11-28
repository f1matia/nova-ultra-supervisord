FROM python:3.11-slim

# Install system deps and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential supervisor && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python requirements and install
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Ensure supervisord.conf is used as the main config
RUN mkdir -p /etc/supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
