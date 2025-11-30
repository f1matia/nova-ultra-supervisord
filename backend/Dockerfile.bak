services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file: ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      pg:
        condition: service_started
      weaviate:
        condition: service_started
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8000/healthz || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 20
      start_period: 5s

